import csv
import os
from common import get, generate_network_filter
from collections import defaultdict

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

def write_user_preferences_file(filename: str, users_games: dict[str, set[str]], start_index=0):
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

    users_games_filename = "../data/users/test.csv"
    write_user_preferences_file(users_games_filename, users_games)

if __name__ == "__main__":
    main()
