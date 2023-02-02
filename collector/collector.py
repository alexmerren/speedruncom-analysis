import requests
import time 

from srcomapi import srcomapi
from . import collector_base 
from datetime import timedelta, datetime

FINAL_DATE = datetime(2023, 1, 1)

class GameInformationCollector:
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        pass

class RelatedGamesCollector:
    def __init__(self, name: str) -> None:
        base = collector_base.CollectorBase(debug=0)
        name = name.replace(" ", "_", -1).lower()
        self.api = Collector(base, f"data/related_games/{name}.csv")
        self.game_id = base.get_game_id(name)

    def run(self, start_index=0) -> None:
        self.api.get_players_related_games(self.game_id, start_index)

class WorldRecordHistoryCollector:
    def __init__(self, name: str) -> None:
        base = collector_base.CollectorBase(debug=1)
        name = name.replace(" ", "_", -1).lower()
        self.api = Collector(base, f"data/world_record_history/{name}.csv")
        self.game_id = base.get_game_id(name)
        self.categories = base.get_game(self.game_id).categories

    def run(self, start_date=None, end_date=FINAL_DATE) -> None:
        for category in self.categories:
            self.api.record_history_game_category(self.game_id, category.id, start_date, end_date)

class Collector:
    def __init__(self, base: collector_base.CollectorBase, filename: str) -> None:
        self.base = base
        self.filename = filename

    def record_history_game_category(self, game_id: str, category_id: str, start_date=None, end_date=FINAL_DATE) -> None:
        game = self.base.get_game(game_id)
        category = self.base.get_category(game, category_id)

        # If a start date is not specified, we go from when the game was released.
        if start_date == None:
            start_date = datetime.strptime(game.data['release-date'], "%Y-%m-%d")

        with open(self.filename, 'a') as openfile:
            openfile.write("game_name,game_id,category_name,category_id,date,user_id,run_id,time\n")

            # Add a week from the release date to allow a run to be on the board.
            current_date = start_date + timedelta(weeks=1)

            while current_date < end_date:
                run_data = self.base.get_top_of_leaderboard(game_id, category.id, current_date).data

                try:
                   run_data = run_data["runs"][0]["run"]
                except IndexError:
                    # We only encounter this error if there are no records on the given date.
                    # This happens if the category hasn't been invented on the date we select.
                    current_date += timedelta(weeks=1)
                    continue

                run_id = run_data["id"]
                time = run_data["times"]["primary_t"]
                users = run_data["players"]

                for user in users :
                    user_id = user.get("name") if user.get("id") is None else user.get("id")
                    openfile.write(f"{game.name},{game.id},{category.name},{category.id},{current_date.isoformat()},{user_id},{run_id},{time}\n")

                current_date += timedelta(weeks=1)

    def get_players_for_game(self, game_id: str) -> list[str]:
        game = self.base.get_game(game_id)
        runs_uri = game.data.get("links")[1].get("uri")
        max_runs = 200

        player_ids = set()

        for category in game.categories:
            verified_runs_uri = f"{runs_uri}&category={category.id}&max={max_runs}&status=verified&orderby=date&direction=asc"
            more_pages = True

            while more_pages:
                print(verified_runs_uri)
                response = requests.get(verified_runs_uri)

                if response.status_code == 420:
                    time.sleep(2)
                    print("420: request limit hit, sleeping for 2s...")
                    response = requests.get(verified_runs_uri)
                if response.status_code == 404:
                    print("404: something went wrong, exiting...")
                    print(response.json())

                response_data = response.json()
                for runs in response_data.get("data"):
                    for player in runs.get("players"):
                        player_id = player.get("id")
                        if player_id == None:
                            break
                
                        player_ids.add(player_id)
                
                if response_data.get("pagination").get("size") < max_runs:
                    more_pages = False

                for link in response_data.get("pagination")["links"]:
                    if link["rel"] == "next":
                        verified_runs_uri = link["uri"]
        print(len(player_ids))
        return list(player_ids)

    def get_players_related_games(self, game_id: str, start_index=0) -> None:
        game = self.base.get_game(game_id)
        player_ids = self.get_players_for_game(game_id)
        all_player_ids_length = len(player_ids)

        with open(self.filename, 'a') as openfile:
            openfile.write(f"HEADER\ngame={game.name},number={all_player_ids_length}\nDATA\n")
            openfile.write("user_id,game_id,game_name,category_id,category_name,level_id,level_name,position\n")
        
            for index, user_id in enumerate(player_ids[start_index:]):
        
                print(f"total={all_player_ids_length},num={index+start_index},user={user_id}")
        
                pb_uri = self.base.get_user(user_id).data["links"][3]["uri"]
                pb_response = requests.get(pb_uri)
        
                # 420 is the response code if you hit the request limit.
                # If user_runs is none, then something fucked up has happened outside our control.
                if pb_response.status_code == 420:
                    print(f"err='hit request limit. Sleeping for 2, then requesting again...'")
                    time.sleep(2)
                    pb_response = requests.get(pb_uri)
        
                user_runs = pb_response.json().get("data")
                if user_runs == None:
                    print(f"err='could not get data field',time={time.ctime()},res={pb_response}")
        
                for run in user_runs:
                    position = run["place"]
                    game_id = run["run"]["game"]
                    category_id = run["run"]["category"]
                    level_id = run["run"]["level"]
        
                    game = self.base.get_game(game_id)
                    category_name = self.base.get_category(game,category_id).name
                    level_name = "None"
                    if level_id != None:
                        level_name = srcomapi.datatypes.Level(self.base.api, data=self.base.api.get("levels/{}".format(level_id))).data["name"]
        
                    openfile.write(f"{user_id},{game_id},{game.name},{category_id},{level_id},{level_name},{category_name},{position}\n")
