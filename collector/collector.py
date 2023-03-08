import time 
import srcomapi
import csv
import math
import os

from datetime import timedelta, datetime
from collections import defaultdict

from . import collector_base 

FINAL_DATE = datetime(2023, 1, 1)

class GameInformationCollector:
    """
    A class designed to collect basic information for every game and write to csv.
    """
    def __init__(self, name:str, debug=0) -> None:
        base = collector_base.CollectorBase(debug=debug)
        name = name.replace(" ", "_", -1).lower()
        self.api = Collector(base, f"data/games_information/{name}.csv", debug=debug)

    def run(self, start_index=0) -> None:
        self.api.get_all_games_with_info(start_index)

class RelatedGamesInformationCollater:
    def __init__(self, name: str, debug=0):
        base = collector_base.CollectorBase(debug=debug)
        self.debug = debug
        name = name.replace(" ", "_", -1).lower()
        self.api = Collector(base, f"data/related_games/{name}.csv")

    def run(self, percentage_limit):
        self.api.collect_all_related_games_data(percentage_limit=percentage_limit)

class CollatedRelatedGamesCollector:
    """
    A class to collate all the information about related games and expand upon just the ID's.
    """
    def __init__(self, name:str, debug=0) -> None:
        base = collector_base.CollectorBase(debug=debug)
        self.debug = debug
        name = name.replace(" ", "_", -1).lower()
        self.api = Collector(base, f"data/related_games/{name}.csv")

    def run(self, game_start_index=0, user_start_index=0) -> None:
        self.api.get_expanded_user_related_games_for_all_games(game_start_index, user_start_index)

class IndividualRelatedGamesCollector:
    """
    A class designed to collect all users' played games for every game.
    """
    def __init__(self, name: str, debug=0) -> None:
        base = collector_base.CollectorBase(debug=debug)
        self.debug = debug
        self.api = Collector(base, f"data/related_games/{name}.csv", debug=debug) 

    def run(self, game_id:str, user_start_index=0) -> None:
        self.api.get_users_related_games_for_game(game_id, user_start_index)

class WorldRecordHistoryCollector:
    """
    A class designed to collect world record history for every game from it's
    release date to the cutoff date
    """
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
    """
    A base class that houses the functions used by the feature classes. This is
    done so that they can share common functionality on top of the base class.
    """
    def __init__(self, base: collector_base.CollectorBase, filename: str, debug=0) -> None:
        self.base = base
        self.debug = debug
        self.filename = filename

    def record_history_game_category(self, game_id: str, category_id: str, start_date=None, end_date=FINAL_DATE) -> None:
        """
        Get the record history from release until cutoff date for a category of
        a game.
        """
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

    def get_user_ids_for_game(self, game_id: str) -> list[str]:
        if game_id == "y65797de": # Subway surfers is cursed rn
            return []

        user_ids = set()
        game = self.base.get_game(game_id)
        for category in game.categories:
            if category.type == 'per-level':
                for level in game.levels:
                    leaderboard = srcomapi.datatypes.Leaderboard(self.base.api, data=self.base.api.get("leaderboards/{}/level/{}/{}?embed=variables".format(game.id, level.id, category.id)))
                    for run in leaderboard.runs:
                        users = run["run"].data["players"]
                        for user in users:
                            if user["rel"] == "user":
                                user_ids.add(user['id'])
            else:
                leaderboard = srcomapi.datatypes.Leaderboard(self.base.api, data=self.base.api.get("leaderboards/{}/category/{}?embed=variables".format(game.id, category.id)))
                for run in leaderboard.runs:
                    users = run["run"].data["players"]
                    for user in users:
                        if user["rel"] == "user":
                            user_ids.add(user['id'])

        return list(user_ids)

    def get_number_of_users_guests_for_game(self, game_id: str) -> tuple[int, int]:
        if game_id == "y65797de": # Subway surfers is cursed rn
            return (-999, -999)

        if game_id in ["k6qw78o6"]: # 404 Not found
            return -1

        user_ids, guest_ids = set(), set()
        game = self.base.get_game(game_id)

        for category in game.categories:
            if category.type == 'per-level':
                for level in game.levels:
                    leaderboard = srcomapi.datatypes.Leaderboard(self.base.api, data=self.base.api.get("leaderboards/{}/level/{}/{}?embed=variables".format(game.id, level.id, category.id)))
                    for run in leaderboard.runs:
                        users = run["run"].data["players"]
                        for user in users:
                            if user["rel"] == "user":
                                user_ids.add(user['id'])
                            else:
                                guest_ids.add(user['name'])
            else:
                leaderboard = srcomapi.datatypes.Leaderboard(self.base.api, data=self.base.api.get("leaderboards/{}/category/{}?embed=variables".format(game.id, category.id)))
                for run in leaderboard.runs:
                    users = run["run"].data["players"]
                    for user in users:
                        if user["rel"] == "user":
                            user_ids.add(user['id'])
                        else:
                            guest_ids.add(user['name'])
                                
        return (len(user_ids), len(guest_ids))

    def get_num_runs_from_stats_page(self, game_id: str) -> int:
        if game_id in ["k6q4rqzd", "yd4ke0p6", "yd4kwop6", "9dowpwe1", "36980y8d", "w6jq8x1j", "lde3jkx6", "j1lq9je6", "369pkl01", "9do8j8o1", "pdvzyqv6"]: # 504 timeout on gamestats page
            return -999

        if game_id in ["k6qw78o6"]: # 404 Not Found
            return -1

        game = self.base.get_game(game_id)
        weblink = game.data.get("weblink")
        gamestats_weblink = f"{weblink}/gamestats"
        response = self.base.get_text(gamestats_weblink)
        if response == None:
            return -999

        start_index = response.find("Number of runs")
        response_section = response[start_index+65:start_index+80]
        numbers = response_section.split()
        return int(numbers[0].replace(',', ''))

    def get_users_related_games_for_all_games(self, game_start_index=0, user_start_index=0) -> None:
        """
        Get all the games that a user has submitted runs for for every game.
        """
        all_game_ids = self.get_all_game_ids()
        total_len = len(all_game_ids)
        if self.debug >= 1: print(total_len)

        for index, game_id in enumerate(all_game_ids[game_start_index:]):
            if self.debug >= 1: print(f"game_index={game_start_index+index},total={total_len},{game_id=}")
            game_name = self.base.get_game(game_id).name
            game_name = game_name.replace(" ", "_", -1).replace("/", '_', -1).lower()
            writeApi = Collector(self.base, f"data/related_games/{index+game_start_index:05}_{game_name}.csv", debug=1)
            writeApi.get_users_related_games_for_game(game_id, user_start_index)
            user_start_index = 0
    
    def get_expanded_user_related_games_for_all_games(self, game_start_index=0, user_start_index=0) -> None:
        all_game_ids = self.get_all_game_ids()
        total_len = len(all_game_ids)
        if self.debug >= 1: print(total_len)
        for index, game_id in enumerate(all_game_ids[game_start_index:]):
            if self.debug >= 1: print(f"game_index={game_start_index+index},total={total_len},{game_id=}")
            self.get_expanded_users_related_games_for_game(game_id, user_start_index)
            user_start_index = 0


    def get_users_related_games_for_game(self, game_id: str, start_index=0) -> None:
        """
        Get all the games that a user has submitted runs for for a single game.
        """
        original_game_id = game_id
        user_ids = self.get_user_ids_for_game(game_id)
        all_user_ids_length = len(user_ids)

        with open(self.filename, 'a') as openfile:
            openfile.write("original_game_id,user_id,game_id,category_id,level_id,position\n")
        
            for index, user_id in enumerate(user_ids[start_index:]):
        
                if self.debug >= 1: print(f"user_index={index+start_index},total={all_user_ids_length},{user_id=}")
        
                pb_uri = self.base.get_user(user_id).data["links"][3]["uri"]
                response_data = self.base.get(pb_uri)
                if response_data == None:
                    return
        
                user_runs = response_data.get("data")
                if user_runs == None:
                    if self.debug >= 1: print(f"user_runs is None,{time.ctime()=},{response_data=}")
                    return
        
                for run in user_runs:
                    position = run["place"]
                    game_id = run["run"]["game"]
                    category_id = run["run"]["category"]
                    level_id = run["run"]["level"]
        
                    openfile.write(f"{original_game_id},{user_id},{game_id},{category_id},{level_id},{position}\n")

    def get_all_game_ids(self) -> list[str]:
        """
        Get a time-ordered (ascending) list of game id's for every game.
        """
        bulk_game_uri = "https://www.speedrun.com/api/v1/games?_bulk=yes&max=1000&orderby=released&direction=asc"
        max_games = 1000
        game_ids = []

        more_pages = True

        while more_pages:
            #if self.debug >= 1: print(bulk_game_uri)
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
        """
        Get basic information about a game like release date and number of runs
        for a game.
        """
        game_ids = self.get_all_game_ids()
        if self.debug >= 1: print(len(game_ids))

        with open(self.filename, 'a') as openfile:
            openfile.write("game_id,game_name,release_date,created_date,num_categories,num_levels,num_runs,num_users,num_guests\n")

            for index, game_id in enumerate(game_ids[start_index:]):
                if self.debug >= 1: print(f"index={index+start_index},len={len(game_ids)},{game_id=}")
                game = self.base.get_game(game_id)
                game_name = game.name.replace(",", " ", -1)
                release_date = game.release_date
                created_date = game.created
                num_categories = len(game.categories)
                num_levels = len(game.levels)
                num_runs = self.get_num_runs_from_stats_page(game_id)
                num_users, num_guests = self.get_number_of_users_guests_for_game(game_id)

                developers = "None"
                if len(game.data["developers"]) == 1:
                    developers = game.developers[0].id
                if len(game.data["developers"]) > 1:
                    developers = f"\"{','.join([developer.id for developer in game.developers])}\""

                openfile.write(f"{game_id},{game_name},{developers},{release_date},{created_date},{num_categories},{num_levels},{num_runs},{num_users},{num_guests}\n")

    def collect_all_related_games_data(self, percentage_limit=1) -> None:
        path = "data/related_games/"
        filenames = []
        with os.scandir(path) as directory:
            for file in directory:
                if file.name.endswith('.csv') and file.is_file():
                    filenames.append(file)

        limit = math.floor(len(filenames) * percentage_limit)

        sourcetarget_to_number = defaultdict(int) 
        for file in filenames[:limit]:
            with open(file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    if len(row) < 3:
                        continue
                    sourcetarget = ' '.join([row[0],row[2]])
                    sourcetarget_to_number[sourcetarget] += 1
                    
        print(len(sourcetarget_to_number))

        with open(f"{self.filename}", 'w') as openfile:
            for key, value in sourcetarget_to_number.items():
                split_key = key.split(' ')
                source = split_key[0]
                target = split_key[1]
                openfile.write(f"{source},{target},{value}\n")
