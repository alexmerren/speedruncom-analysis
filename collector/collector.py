import time 

from datetime import timedelta, datetime

from . import collector_base 

FINAL_DATE = datetime(2023, 1, 1)

class GameInformationCollector:
    def __init__(self, name:str) -> None:
        base = collector_base.CollectorBase(debug=0)
        name = name.replace(" ", "_", -1).lower()
        self.api = Collector(base, f"data/games_information/{name}.csv")
        self.game_id = base.get_game_id(name)

    def run(self, start_index=0) -> None:
        self.api.get_all_games_with_info(start_index)

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
        runs_uri = game.data.get("links")[1]["uri"]
        max_runs = 200

        player_ids = set()

        for category in game.categories:
            verified_runs_uri = f"{runs_uri}&category={category.id}&max={max_runs}&status=verified&orderby=date&direction=asc"
            more_pages = True

            while more_pages:
                print(verified_runs_uri)
                response_data = self.base.get(verified_runs_uri)
                if response_data == None:
                    return []

                # This will be hit if there are too many pages and we try and go past the pagination limit.
                if response_data.get("status") == 400:
                    return []

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

        return list(player_ids)

    def get_number_of_players_for_game(self, game_id: str) -> int:
        """
        For this function, we have a couple of specific return states:
        -999: This will return if we have too many runs so that we go past the pagination limit.
        -1: If there's a general error so we will have to re run for this given game.
        """
        game = self.base.get_game(game_id)
        runs_uri = game.data.get("links")[1]["uri"]
        max_runs = 200

        number = 0

        for category in game.categories:
            verified_runs_uri = f"{runs_uri}&category={category.id}&max={max_runs}&status=verified&orderby=date&direction=asc"
            more_pages = True

            while more_pages:
                print(verified_runs_uri)
                response_data = self.base.get(verified_runs_uri)
                if response_data == None:
                    return -1

                # This will be hit if there are too many pages and we try and go past the pagination limit.
                if response_data.get("status") == 400:
                    print(response_data)
                    return -999

                for _ in response_data.get("data"):
                    number += 1
                
                if response_data.get("pagination").get("size") < max_runs:
                    more_pages = False

                for link in response_data.get("pagination")["links"]:
                    if link["rel"] == "next":
                        verified_runs_uri = link["uri"]

        return number

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
                response_data = self.base.get(pb_uri)
                if response_data == None:
                    return
        
                user_runs = response_data.get("data")
                if user_runs == None:
                    print(f"user_runs is None,{time.ctime()=},{response_data=}")
        
                for run in user_runs:
                    position = run["place"]
                    game_id = run["run"]["game"]
                    category_id = run["run"]["category"]
                    level_id = run["run"]["level"]
        
                    game = self.base.get_game(game_id)
                    category_name = self.base.get_category(game,category_id).name
                    level_name = "None"
                    if level_id != None:
                        level_name = self.base.get_level(level_id)
        
                    openfile.write(f"{user_id},{game_id},{game.name},{category_id},{level_id},{level_name},{category_name},{position}\n")

    def get_all_games(self) -> list[str]:
        bulk_game_uri = "https://www.speedrun.com/api/v1/games?_bulk=yes&max=1000&orderby=released&direction=asc"
        max_games = 1000
        game_ids = []

        more_pages = True

        while more_pages:
            print(bulk_game_uri)
            response_data = self.base.get(bulk_game_uri)
            if response_data == None:
                return []

            for game in response_data.get("data"):
                game_ids.append(game["id"])
            
            if response_data.get("pagination").get("size") < max_games:
                more_pages = False

            for link in response_data.get("pagination")["links"]:
                if link["rel"] == "next":
                    bulk_game_uri = link["uri"]

        return game_ids

    def get_all_games_with_info(self, start_index=0):
        game_ids = self.get_all_games()

        with open(self.filename, 'a') as openfile:
            openfile.write("game_id,game_name,release_date,created_date,num_runs\n")

            for index, game_id in enumerate(game_ids[start_index:]):
                print(f"index={index+start_index},{game_id=}")
                game = self.base.get_game(game_id)
                game_name = game.name
                release_date = game.release_date
                created_date = game.created
                num_runs = self.get_number_of_players_for_game(game_id)
                openfile.write(f"{game_id},{game_name},{release_date},{created_date},{num_runs}\n")
