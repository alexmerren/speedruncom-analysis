import csv
import os

from datetime import datetime
from collections import defaultdict

FINAL_DATE = datetime(2023, 1, 1)

def generate_games_filter(filename: str):
    with open(filename, 'r', encoding='utf-8') as openfile:
        csv_reader = csv.reader(openfile)
        next(csv_reader)
        filter_map = defaultdict(bool)
        for row in csv_reader:
            # Check if the created/release date is after 2023, if it is then we can ignore it in the network.
            release_date = datetime.strptime(row[3], "%Y-%m-%d")
            if row[4] == "None": row[4] = "2017-10-22T05:21:29Z" # This is a completely random date before the final date.
            created_date = datetime.strptime(row[4], "%Y-%m-%dT%H:%M:%SZ")

            # Cannot get accurate information about subway surfers so I am just *not*.
            disallowed_games = ["y65797de"]

            if created_date < FINAL_DATE and release_date < FINAL_DATE and \
                row[0] not in disallowed_games and row[1] not in disallowed_games:
                filter_map[row[0]] = True

    return filter_map

def generate_user_preferences_from_raw(directory: str, filter=None):
    filenames = []
    with os.scandir(directory) as dir:
        for file in dir:
            if file.name.endswith('.csv') and file.is_file():
                filenames.append(file)
    
    users_games = defaultdict(set)
    for file in filenames:
            with open(file, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                # Skip the header of each csv file.
                next(csv_reader)

                for row in csv_reader:
                    users_games[row[1]].add(row[2])

    return users_games

def write_user_preferences_file(filename: str, users_games: dict[str, set[str]]):
    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("user,games\n")
        for user_id, game_ids in users_games.items():
            games = f"\"{','.join(game_ids)}\""
            openfile.write(f"{user_id},{games}\n")

def main():
    filter_filename = "../data/games/metadata/all_games.csv"
    filter_map = generate_games_filter(filter_filename)

    related_games_directory = "../data/games/network_raw/"
    users_games = generate_user_preferences_from_raw(related_games_directory, filter=filter_map)

    users_games_filename = "../data/users/user_games_preferences.csv"
    write_user_preferences_file(users_games_filename, users_games)

if __name__ == "__main__":
    main()
