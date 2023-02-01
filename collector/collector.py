from . import collector_base 

import requests

from datetime import timedelta, datetime

FINAL_DATE = datetime(2023, 1, 1)

class RelatedGamesCollector:
    def __init__(self, name: str) -> None:
        base = collector_base.CollectorBase(debug=1)
        name = name.replace(" ", "_", -1).lower()
        self.api = Collector(base, f"data/related_games/{name}.csv")
        self.game_id = base.get_game_id(name)
        self.categories = base.get_game(self.game_id).categories

    def run(self) -> None:
        for category in self.categories:
            self.api.get_players_related_games(self.game_id, category.id)

class WorldRecordHistoryCollector:
    def __init__(self, name: str) -> None:
        base = collector_base.CollectorBase(debug=1)
        name = name.replace(" ", "_", -1).lower()
        self.api = Collector(base, f"data/world_record_history/{name}.csv")
        self.game_id = base.get_game_id(name)
        self.categories = base.get_game(self.game_id).categories

    def run(self) -> None:
        for category in self.categories:
            self.api.record_history_game_category(self.game_id, category.id)

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

    def get_players_related_games(self, game_id: str, category_id: str) -> None:
        original_game = self.base.get_game(game_id)
        category = self.base.get_category(original_game, category_id)
        runs = self.base.get_leaderboard(original_game.id, category.id, FINAL_DATE).data["runs"]

        players = []
        for run in runs:
            players.append(run["run"]["players"])

        user_ids = []
        for entry in players:
            for user in entry:

                user_id = user.get("id")
                if user_id == None:
                    break
                user_ids.append(user_id)

        with open(self.filename, 'a') as openfile:
            openfile.write(f"HEADER\ngame={original_game.name},number={len(user_ids)}\nDATA\n")
            openfile.write("user_id,game_id,game_name,category_id,category_name,position\n")

            for user_id in user_ids:
                pb_uri = self.base.get_user(user_id).data["links"][3]["uri"]
                pb_response = requests.get(pb_uri)
                user_runs = pb_response.json()["data"]
                for run in user_runs:
                    position = run["place"]
                    game_id = run["run"]["game"]
                    category_id = run["run"]["category"]

                    game = self.base.get_game(game_id)
                    category_name = self.base.get_category(game,category_id).name

                    openfile.write(f"{user_id},{game_id},{game.name},{category_id},{category_name},{position}\n")

