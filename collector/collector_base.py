import srcomapi
import requests
import time

REQUEST_LIMIT_SLEEP_TIME = 2

class CollectorBase:
    def __init__(self, debug=0) -> None :
        self.api = srcomapi.SpeedrunCom()
        self.api.debug = debug 
        self.game_cache = {}

    def get_game_id(self, name) -> str :
        game = self.api.search(srcomapi.datatypes.Game, {"name": name})[0]
        return game.id

    def get_game(self, game_id) -> srcomapi.datatypes.Game :
        game = self.game_cache.get(game_id)
        if game != None:
            return game
        self.game_cache[game] = self.api.get_game(game_id)
        return self.game_cache[game] 

    def get_category_id(self, game, category_name) -> str:
        for category in game.categories:
            if category_name == category.name:
                return str(category.id)
        return ""

    def get_category(self, game, category_id) -> srcomapi.datatypes.Category:
        for category in game.categories:
            if category_id == category.id:
                return category
        return None

    def get_level(self, level_id: str) -> srcomapi.datatypes.Level:
        return srcomapi.datatypes.Level(self.api, data=self.api.get("levels/{}".format(level_id)))

    def get_user(self, user_id) -> srcomapi.datatypes.User:
        return self.api.get_user(user_id)

    def get_leaderboard(self, game_id, category_id, date) -> srcomapi.datatypes.Leaderboard:
        return srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables&date={}".format(game_id, category_id, date.isoformat())))

    def get_top_of_leaderboard(self, game_id, category_id, date) -> srcomapi.datatypes.Leaderboard:
        return srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables&top=1&date={}".format(game_id, category_id, date.isoformat())))

    def search(self):
        pass

    def get(self, uri: str):
        response = requests.get(uri)
        if response.status_code == 404:
            print(f"404 (Not Found): Exiting, {response.json()=}")
            return None
        if response.status_code == 420:
            print(f"420 (Request limit): Sleeping for {REQUEST_LIMIT_SLEEP_TIME}s, then requesting again.")
            time.sleep(REQUEST_LIMIT_SLEEP_TIME)
            response = requests.get(uri)

        return response.json()

