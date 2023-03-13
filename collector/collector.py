import time 
import srcomapi
import csv
import math
import os

from datetime import timedelta, datetime
from collections import defaultdict

from . import collector_base 

FINAL_DATE = datetime(2023, 1, 1)
"""datetime: cutoff date for new information being collected."""

class GameMetadataCollector:
    """A class designed to collect basic information for every game and write to csv.

    In the name, we replace spaces with underscores and converted to all
    lowercase. It then saves the file in the `data/games/metadata` directory.

    Attributes:
        api (collctor_base): The base collector object for interacting with the speedrun.com API.

    Args:
        name (str): The name of the file to be saved. 
        debug (int): The debug value of the collector base module.

    """

    def __init__(self, name:str, debug=0):
        base = collector_base.CollectorBase(debug=debug)
        name = escape_filename(name)
        self.api = Collector(base, f"data/games/metadata/{name}.csv", debug=debug)

    def run(self, start_index=0):
        """Start the collection process of writing to file with an optional start index.

        Args:
            start_index (int): The start index of the list of games in the metadata file. The index is printed during the process of collection.

        """

        self.api.get_all_games_with_info(start_index)

class RelatedGamesInformationCollater:
    """A class for going through previously collected related games information and collating it into one file.

    In the name, we replace spaces with underscores and converted to all
    lowercase. It then saves the file in the `data/too_big/` directory.
    Generally, once the file is generated and we find that the file is big
    enough to be checked into version control, we move the file to a tracked
    directory.

    Attributes:
        api (collctor_base): The base collector object for interacting with the speedrun.com API.

    Args:
        name (str): The name of the file to be saved. 

    """
    
    def __init__(self, name: str, debug=0):
        base = collector_base.CollectorBase(debug=debug)
        self.debug = debug
        name = escape_filename(name)
        self.api = Collector(base, f"data/too_big/{name}.csv")

    def run(self, percentage_limit: float):
        """Start the collation process of writing to file with an optional percentage limit.
        
        Args:
            percentage_limit (float): The percentage of the files that should be collated.

        """
        
        self.api.collect_all_related_games_data(percentage_limit=percentage_limit)

class MultipleRelatedGamesCollector:
    """A class for collecting users' played games for several games. 

    Writes multiple files within the `data/games/network_raw/` directory with
    the structure `<index>_<game name>.csv`. There is no `name` argument as
    another writeApi is created within the run function.

    Attributes:
        api (Collector): A class for calling the feature functions below.

    Args:
        debug (int): A debug value for the collector base class.

    """

    def __init__(self, debug=0):
        base = collector_base.CollectorBase(debug=debug)
        self.debug = debug
        self.api = Collector(base, f"")

    def run(self, game_start_index=0, user_start_index=0):
        """Start the collection process for multiple games.

        Args:
            game_start_index (int): A start index for the list of games. This specifies which file the function start at.
            user_start_index (int): A start index for the users of a game. This specifies where in a file the function starts at.

        """

        self.api.get_users_related_games_for_all_games(game_start_index, user_start_index)

class IndividualRelatedGamesCollector:
    """ A class to collect all users' played games for a single game.


    
    Attributes:
        api (Collector): A class for calling the feature functions below.

    Args:
        name (str): The filename to write to.
        debug (int): The debug value for the CollectorBase class interacting with speedrun.com API.

    """

    def __init__(self, name: str, debug=0):
        base = collector_base.CollectorBase(debug=debug)
        self.debug = debug
        name = escape_filename(name)
        self.api = Collector(base, f"data/games/network_raw/{name}.csv", debug=debug) 

    def run(self, game_id:str, user_start_index=0):
        """
        """
        self.api.get_users_related_games_for_game(game_id, user_start_index)

class WorldRecordHistoryCollector:
    """ A class to collect world record history for every game.
    """
    def __init__(self, name: str):
        base = collector_base.CollectorBase(debug=1)
        name = escape_filename(name)
        self.api = Collector(base, f"data/games/world_record_history/{name}.csv")
        self.game_id = base.get_game_id(name)
        self.categories = base.get_game(self.game_id).categories

    def run(self, start_date=None, end_date=FINAL_DATE):
        for category in self.categories:
            self.api.record_history_game_category(self.game_id, category.id, start_date, end_date)

class Collector:
    """ A base class that encapsulates the functions used by the feature classes. 

    Args:
        base (collector_base.CollectorBase): A base class used to interact with the speedrun.com API.
        filename (str): A filename used for writing to file in the member functions.
        debug (int): A debug flag for printing operational statements.

    Attributes:
        base (collector_base.CollectorBase): A base class used to interact with the speedrun.com API.
        filename (str): A filename used for writing to file in the member functions.

    """

    def __init__(self, base: collector_base.CollectorBase, filename: str, debug=0):
        self.base = base
        self.debug = debug
        self.filename = filename

    def record_history_game_category(self, game_id: str, category_id: str, start_date=None, end_date=FINAL_DATE):
        """ Get the record history from release until cutoff date for a category of a game.

        Iterate through each week from start_date until end_date and write the
        top entry of the leaderboard to a file named in self.filename. If
        start_date is not specified in the arguments then the start_date is set
        as the release date of the game according to the speedrun.com API.

        Args:
            game_id (str): A valid game ID from speedrun.com
            category_id (str): A valid category ID from speedrun.com and belongs to the game specified earlier in game_id.
            start_date (datetime): A datetime of the start date of the world record history collection.
            end_date (datetime): A datetime of the end date of the world record history collection.

        """

        game = self.base.get_game(game_id)
        category = self.base.get_category(game, category_id)

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
        """Gets a list of user IDs that have played a given game.

        This function uses the method outlined in the README of the srcomapi
        package on github (https://github.com/blha303/srcomapi).

        Args:
            game_id (str): A valid game ID found from speedrun.com

        Returns:
            A list of strings containing user IDs.

        """

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
        """Find the number of users and guests that have played a game.

        This function goes through the leaderboards of a game and finds the
        number of users and guests that have played a game. If a game cannot be
        found by the API, it returns (-1, -1).

        Args:
            game_id (str): A valid game ID found from speedrun.com.

        Returns:
            The number of users and guests as a tuple of ints: (number of users, number of guests). If the game_id is invalid, it returns (-1, -1).

        """

        if game_id in ["k6qw78o6"]: # 404 Not found
            return (-1, -1)

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
        """Find the number of runs for a given game through the stats page.

        There are a few games that have malfunctioning gamestats pages. If the
        game_id matches any of these, the function returns `-999.` If there are
        games that cannot be found by the API, then the functions returns `-1`.

        Args:
            game_id (str): A valid game ID retrieved from speedrun.com.

        Returns:
            The number of runs for a given game as an int.

        """

        if game_id in ["k6q4rqzd", "yd4ke0p6", "yd4kwop6", "9dowpwe1", "36980y8d", "w6jq8x1j", "lde3jkx6", "j1lq9je6", "369pkl01", "9do8j8o1", "pdvzyqv6"]:
            return -999

        if game_id in ["k6qw78o6"]:
            return -1

        game = self.base.get_game(game_id)
        weblink = game.data.get("weblink")
        gamestats_weblink = f"{weblink}/gamestats"
        response = self.base.get_text(gamestats_weblink)
        if response == None:
            return -1

        start_index = response.find("Number of runs")
        response_section = response[start_index+65:start_index+80]
        numbers = response_section.split()
        return int(numbers[0].replace(',', ''))

    def get_users_related_games_for_all_games(self, game_start_index=0, user_start_index=0):
        """Call get_users_related_games_for_game for all games found on speedrun.com.

        Loop through all the games found on speedrun.com and write the personal
        bests for each user that plays a given game. We create a `writeApi`
        class with a formatted filename with the structure `<index>_<game
        name>.csv`. The user_start_index is changed to 0 after moving to a new
        game.

        Args:
            game_start_index (int): The start index of the list of games. This denotes which file to start at.
            user_start_index (int): The start index of the list of users for a game. This denotes *how far through* a file you should start at.
        
        """

        all_game_ids = self.get_all_game_ids()
        total_len = len(all_game_ids)
        if self.debug >= 1: print(total_len)

        for index, game_id in enumerate(all_game_ids[game_start_index:]):
            if self.debug >= 1: print(f"game_index={game_start_index+index},total={total_len},{game_id=}")
            game_name = self.base.get_game(game_id).name
            game_name = escape_filename(game_name)
            writeApi = Collector(self.base, f"data/games/network_raw/{index+game_start_index:05}_{game_name}.csv", debug=1)
            writeApi.get_users_related_games_for_game(game_id, user_start_index)
            user_start_index = 0

    def get_users_related_games_for_game(self, game_id: str, start_index=0):
        """Get a list of personal bests for each user that has played a game.

        We loop through each user that has played a game given a game ID and
        write their personal bests to a CSV file named in self.filename. If
        attempting to retrieve a non-existent user, the function returns
        nothing and stops prematurely.

        Args:
            game_id (str): A valid game ID retrieved from speedrun.com
            start_index (int): A start index for a list of users.

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
        """Get a time-ordered ascending list of game ids of games found on speedrun.com.

        Loops through the games API URL with bulk mode enabled. There are
        approx. 33,000 games as of March 2023.

        Returns:
            A list of strings containing the game IDs on speedrun.com

        """

        bulk_game_uri = "https://www.speedrun.com/api/v1/games?_bulk=yes&max=1000&orderby=released&direction=asc"
        max_games = 1000
        game_ids = []

        more_pages = True

        while more_pages:
            if self.debug >= 1: print(bulk_game_uri)
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
        """Loop through all games and write basic information about each to a csv.

        Go through a list of game IDs and write to a CSV defined in self.filename.

        Args:
            start_index (int): The start index of the games found in the list of all game IDs.

        """

        game_ids = self.get_all_game_ids()
        if self.debug >= 1: print(len(game_ids))

        with open(self.filename, 'a', encoding='utf-8') as openfile:
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

    def collect_all_related_games_data(self, percentage_limit=1.0):
        """Collate all the data from `data/games/network_raw/` into a single file.

        Searches through the `data/games/network_raw/` directory for all the
        files ending in `.csv`. Writes to a file named in the self.filename
        attribute. Creates a csv with a `source,target,value` structure. This
        function also removes edges that are self-referential.

        Args:
            percentage_limit (float): A percentage of the files in the `data/games/network_raw/` directory to be parsed.

        """

        path = "data/games/network_raw/"
        filenames = []
        with os.scandir(path) as directory:
            for file in directory:
                if file.name.endswith('.csv') and file.is_file():
                    filenames.append(file)

        limit = math.floor(len(filenames) * percentage_limit)

        sourcetarget_to_number = defaultdict(int) 
        for file in filenames[:limit]:
            with open(file, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    # If there are less than 3 items in a row, skip it (this should never happen ideally).
                    if len(row) < 3:
                        continue
                    sourcetarget = ' '.join([row[0],row[2]])
                    sourcetarget_to_number[sourcetarget] += 1
                    
        print(len(sourcetarget_to_number))

        with open(self.filename, 'w', encoding='utf-8') as openfile:
            openfile.write("source,target,value")
            for key, value in sourcetarget_to_number.items():
                split_key = key.split(' ')
                source = split_key[0]
                target = split_key[1]
                if source == target:
                    continue

                openfile.write(f"{source},{target},{value}\n")

def escape_filename(name: str) -> str:
    """Escapes a string so it can be a valid filename in windows and linux.

    The list of invalid characters for filenames in unix and windows can be
    found here:
    https://stackoverflow.com/questions/1976007/what-characters-are-forbidden-in-windows-and-linux-directory-names

    Args:
        name (str): A string that may contain invalid filename characters.

    Returns:
        A string of an escaped version of the original string.

    """
    for character in ["/", "<", ">", ":", "\"", "/", "\\", "|", "*", "?"]:
        if character in name:
            name = name.replace(character, "", -1)
    
    name = name.replace(" ", "_", -1)
    return name
