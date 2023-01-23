import srcomapi
import psutil

class CollectorBase:
    def __init__(self, debug=0) -> None :
        self.api = srcomapi.SpeedrunCom()
        self.api.debug = debug 

    def get_game_id(self, name) -> str :
        game = self.api.search(srcomapi.datatypes.Game, {"name": name})[0]
        return game.id

    def get_game(self, game_id) -> srcomapi.datatypes.Game :
        return self.api.get_game(game_id)

    def get_category_id(self, game, category_name) -> str:
        for category in game.categories:
            if category_name == category.name:
                return str(category.id)
        return ""

    def get_category(self, game, category_id) -> srcomapi.datatypes.Category:
        for category in game.categories:
            if category_id == category.id:
                return category
        return srcomapi.datatypes.Category()


    def get_user(self, user_id) -> srcomapi.datatypes.User:
        return self.api.get_user(user_id)

    def get_leaderboard(self, game_id, category_id, date) -> srcomapi.datatypes.Leaderboard:
        return srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables&date={}".format(game_id, category_id, date.isoformat())))

    def get_top_of_leaderboard(self, game_id, category_id, date) -> srcomapi.datatypes.Leaderboard:
        return srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables&top=1&date={}".format(game_id, category_id, date.isoformat())))

    def print_debug(self):
        print(f"CPU: {psutil.cpu_percent()}%")
        print(f"RAM: {psutil.virtual_memory()[3]/1000000000} GB")

