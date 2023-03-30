import csv
import os
import time

from collections import defaultdict
from datetime import datetime
from requests_cache import CachedSession
from requests.exceptions import JSONDecodeError

FINAL_DATE = datetime(2023, 1, 1)
REQUEST_TIMEOUT_SLEEP = 2

REQUEST_CACHE_NAME = "user_preference_cache"
REQUEST_TIMEOUT_SLEEP = 2

requests_c = CachedSession(
        REQUEST_CACHE_NAME, 
        backend='sqlite',
        expire_after=None)

def generate_network_filter(filename: str) -> dict[str, bool]:
    """Create a dictionary containing the games that we want to include in further analysis.
    
    We check if a game was released/created before the cutoff date, and if the
    game is in a disallowed games list. If the answer to both of these
    questions is no, then we want to include it in our analysis.

    Args:
        filename (str): The name of the games metadata file.

    Returns:
        A dictionary of game ID to boolean. If the game is allowed True, if not False.

    """

    with open(filename, 'r', encoding='utf-8') as openfile:
        csv_reader = csv.reader(openfile)
        next(csv_reader)
        filter_map = defaultdict(bool)
        for row in csv_reader:
            # Check if the created/release date is after 2023, if it is then we can ignore it in the network.
            release_date = datetime.strptime(row[3], "%Y-%m-%d")
            if row[4] == "None":
                row[4] = "2017-10-22T05:21:29Z" # This is a completely random date before the final date.
            created_date = datetime.strptime(row[4], "%Y-%m-%dT%H:%M:%SZ")

            disallowed_games = ["y65797de"]

            if created_date < FINAL_DATE and release_date < FINAL_DATE and \
                row[0] not in disallowed_games and row[1] not in disallowed_games:
                filter_map[row[0]] = True

    return filter_map

def get(uri: str):
    """Get request a URI.

    Run requests through a requests cache defined above. If response code is
    404 or 400, then return None. If response code is 420 or 504, then retry
    after timeout.

    Args:
        uri (str): The URL of a resource.

    Returns:
        JSON of a response body.

    """

    print(uri)
    response = requests_c.get(uri)
    if response.status_code in [404,400]:
        print(f"({response.status_code}) {response.reason}: Exiting. {response.json()=}")
        return None
    if response.status_code in [420,504]:
        print(f"({response.status_code}) {response.reason}: re-requesting.")
        time.sleep(REQUEST_TIMEOUT_SLEEP)
        return get(uri)
    try:
        return response.json()
    except: 
        print(f"({response.status_code}) {response.reason}: re-requesting")
        time.sleep(REQUEST_TIMEOUT_SLEEP)
        return get(uri)

def generate_user_preferences_from_raw(directory: str, filter=None) -> dict[str, set[str]]:
    """Create a file containing the preferences of each user in the `network_raw` directory.

    Find each CSV file within a directory and parse each game a user has played
    from their contents. If a game is not present in the filter, then we ignore
    it.

    Args:
        directory (str): A directory containing all the raw related games files.
        filter (dict[str, bool]): A filter containing which games we allow in our processing.

    Returns:
        A dictionary of user IDs as keys, and a set of game IDs which that user has played.

    """

    filenames = []
    with os.scandir(directory) as dir:
        for file in dir:
            if file.name.endswith('.csv') and file.is_file():
                filenames.append(file)
    
    users_games = defaultdict(set)
    for file in filenames:
            with open(file, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                next(csv_reader)
                for row in csv_reader:
                    if not filter.get(row[2]):
                        continue
                    users_games[row[1]].add(row[2])

    return users_games

def write_user_preferences_file(filename: str, users_games: dict[str, set[str]]):
    """Write the user preferences dictionary to a file with some extra metadata.

    If user ID cannot be found by the API, then the metadata is listed as Null
    instead of None. None represents no data from the API, whereas Null
    represents incorrect/missing data.

    Args:
        filename (str): The filename to write to.
        user_games (dict[str, set[str]]): The dictionary of user IDs to the set of game IDs that those users play.
    """

    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("user,signup_date,location,num_games,games\n")
        for user_id, game_ids in users_games.items():
            games = f"\"{','.join(game_ids)}\""

            
            user_response = get(f"https://www.speedrun.com/api/v1/users/{user_id}")
            if user_response == None:
                openfile.write(f"{user_id},Null,Null,{len(game_ids)},{games}\n")
                continue

            # Optional data
            user_data = user_response.get("data")
            country_code = user_data.get("location")
            if country_code is not None:
                country_code = country_code["country"]["code"]
            signup_date = user_data.get("signup")
            
            openfile.write(f"{user_id},{signup_date},{country_code},{len(game_ids)},{games}\n")


def generate_all_users_from_raw(directory: str, filter_map=None):
    filenames = []
    with os.scandir(directory) as dir:
        for file in dir:
            if file.name.endswith('.csv') and file.is_file():
                filenames.append(file)

    all_users = []
    for file in filenames:
        with open(file, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                all_users.append(row[1])

    return sorted(all_users)

def write_user_runs_file(filename: str, all_users: list[str], start_index: int):
    num_users = len(all_users)
    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("user,num_runs\n")
        for index, user in enumerate(all_users[start_index:]):
            print(f"index={index+start_index},{num_users=},{user=}")
            uri = f"https://www.speedrun.com/api/v1/runs?user={user}&max=200&status=verified"
            more_pages = True
            num_runs = 0
            while more_pages:
                response_data = get(uri)
                if response_data == None:
                    return 

                for run in response_data.get('data'):
                    if datetime.strptime(run.get('date'), '%Y-%m-%d') < FINAL_DATE:
                        num_runs += 1

                if response_data.get("pagination").get("size") < 200:
                    more_pages = False

                for link in response_data.get("pagination")["links"]:
                    if link["rel"] == "next":
                        uri = link["uri"]

            openfile.write(f"{user},{num_runs}")

def generate_user_runs(start_index: int):
    filter_filename = "../data/games/metadata/all_games_srcom.csv"
    filter_map = generate_network_filter(filter_filename)

    related_games_directory = "../data/games/network_raw/"
    all_users = generate_all_users_from_raw(related_games_directory, filter=filter_map)

    users_runs_filename = "../data/users/user_preferences_with_metadata.csv"
    write_user_runs_file(users_runs_filename, all_users, start_index)

def generate_user_preferences():
    filter_filename = "../data/games/metadata/all_games_srcom.csv"
    filter_map = generate_network_filter(filter_filename)

    related_games_directory = "../data/games/network_raw/"
    users_games = generate_user_preferences_from_raw(related_games_directory, filter=filter_map)

    users_games_filename = "../data/users/user_preferences_with_metadata.csv"
    write_user_preferences_file(users_games_filename, users_games)

def main():
    generate_user_runs(start_index=0)

if __name__ == "__main__":
    main()
