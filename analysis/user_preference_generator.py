import csv
import os
from common import get, generate_network_filter
from collections import defaultdict

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

def main():
    filter_filename = "../data/games/metadata/all_games.csv"
    filter_map = generate_network_filter(filter_filename)

    related_games_directory = "../data/games/network_raw/"
    users_games = generate_user_preferences_from_raw(related_games_directory, filter=filter_map)

    users_games_filename = "../data/users/test_2.csv"
    write_user_preferences_file(users_games_filename, users_games)

if __name__ == "__main__":
    main()
