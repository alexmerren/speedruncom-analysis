import srcomapi
import time

from requests_cache import CachedSession

REQUEST_CACHE_NAME = "collector_requests_cache"
REQUEST_TIMEOUT_SLEEP = 2

requests_c = CachedSession(
        REQUEST_CACHE_NAME, 
        backend='sqlite',
        expire_after=None)

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

    def get_top_of_leaderboard(self, game_id, category_id, date, level_id=None) -> srcomapi.datatypes.Leaderboard:
        if level_id != None:
            return srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/level/{}/{}?embed=variables".format(game_id, level_id, category_id)))
        return srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables&top=1&date={}".format(game_id, category_id, date.isoformat())))

    def search(self):
        pass

    def get_text(self, uri: str):
        response = requests_c.get(uri)
        if response.status_code in [404,400]:
            print(f"({response.status_code}) {response.reason}: Exiting. {response.json()=}")
            return None
        if response.status_code in [420,504]:
            print(f"({response.status_code}) {response.reason}: re-requesting.")
            time.sleep(REQUEST_TIMEOUT_SLEEP)
            return self.get(uri)
        try:
            return response.text
        except: 
            print(f"({response.status_code}) {response.reason}: re-requesting")
            time.sleep(REQUEST_TIMEOUT_SLEEP)
            return self.get(uri)

    def get(self, uri: str):
        response = requests_c.get(uri)
        if response.status_code in [404,400]:
            print(f"({response.status_code}) {response.reason}: Exiting. {response.json()=}")
            return None
        if response.status_code in [420,504]:
            print(f"({response.status_code}) {response.reason}: re-requesting.")
            time.sleep(REQUEST_TIMEOUT_SLEEP)
            return self.get(uri)
        try:
            return response.json()
        except: 
            print(f"({response.status_code}) {response.reason}: re-requesting")
            time.sleep(REQUEST_TIMEOUT_SLEEP)
            return self.get(uri)
