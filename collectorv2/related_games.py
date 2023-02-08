import time

import requests_cache

REQUEST_LIMIT_SLEEP_TIME = 3
REQUEST_CACHE_NAME = "srcom_requests_cache"

class RelatedGamesCollector:
    def __init__(self, debug=0):
        self.debug = debug
        self.request_cache = requests_cache.CachedSession(
            REQUEST_CACHE_NAME,
            allowable_methods=['GET'],
            allowable_codes=[200],
        )

    def collect_players_games_for_all_games(self, game_start_index=0, player_start_index=0):
        game_ids = self.get_list_of_all_games()
        for index, game_id in enumerate(game_ids[game_start_index:]):
            if self.debug > 0: print(f"{len(game_ids)=},index={game_start_index+index},{game_id=}")
            user_ids = self.get_list_of_all_user_ids_for_game(game_id)
            for user_id in user_ids:
                runs = self.get_runs_by_user_id()

            player_start_index = 0

    def get_list_of_all_user_ids_for_game(self, game_id) -> list[str]:
        game = self.get_game_by_id(game_id)
        runs_uri = ""
        try:
            runs_uri = game["data"]["links"][1]["uri"]
        except IndexError:
            if self.debug > 0: print("could not get game data")
            return []

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

    def get_list_of_all_games(self) -> list[str]:
        """
        Return a list of all the games on speedrun.com.
        """
        uri = "https://www.speedrun.com/api/v1/games?_bulk=yes&max=1000&orderby=released&direction=asc"
        max_games = 1000
        game_ids = []

        more_pages = True

        while more_pages:
            if self.debug > 0: print(uri)

            response_data = self.get(uri)
            if response_data == None:
                return []

            for game in response_data.get("data"):
                game_ids.append(game["id"])
            
            if response_data.get("pagination").get("size") < max_games:
                more_pages = False

            for link in response_data.get("pagination")["links"]:
                if link["rel"] == "next":
                    uri = link["uri"]

        return game_ids


    def get_game_by_id(self, game_id: str):
        """
        Return the JSON of a request of a game.
        """
        pass

    def get_category_by_id(self, category_id: str):
        """
        Return the JSON of a request of a category.
        """
        pass

    def get_level_by_id(self, level_id: str):
        """
        Return the JSON of a request of a level.
        """
        pass

    def get_runs_by_user_id(self):
        """
        Return the JSON of a request for a user's personal bests.
        """
        pass

    def get(self, uri: str):
        """
        This is a wrapper for a basic request.
        """
        response = self.request_cache.get(uri)
        if response.status_code == 404:
            print(f"404 (Not Found): Exiting, {response.json()=}")
            return None
        if response.status_code == 420:
            print(f"420 (Request limit): Sleeping for {REQUEST_LIMIT_SLEEP_TIME}s, then requesting again.")
            time.sleep(REQUEST_LIMIT_SLEEP_TIME)
            response = self.request_cache.get(uri)

        return response.json()
