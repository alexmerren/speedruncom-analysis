import srcomapi
import time
from datetime import datetime
from requests_cache import CachedSession

REQUEST_CACHE_NAME = "collector_requests_cache"
"""str: The name of the request cache file for this module."""

REQUEST_TIMEOUT_SLEEP = 2
"""int:  The time in seconds for timeout between requests when given a 420 response."""

requests_c = CachedSession(
        REQUEST_CACHE_NAME, 
        backend='sqlite',
        expire_after=None)
"""CachedSession: The requests cache object, all HTTP requests should be done through this cache object."""

class CollectorBase:
    """A base class that interacts with the speedrun.com API in a safe way. Should be used to interact with the API in *any* way. 

    Attributes:
        api (SpeedrunCom): The base API class created by srcomapi module.
    Args:
        debug (int): The debug profile, set to 1 to see URLs accessed, set to 2 to see all internal opeations.

    """

    def __init__(self, debug=0) -> None :
        self.api = srcomapi.SpeedrunCom()
        self.api.debug = debug 

    def get_game_id(self, name: str) -> str :
        """Call the speedrun.com API to fuzzy find the game ID based on the name. 

        Args:
            name (str): Name of a game. 

        Returns:
            String ID of the game from speedrun.com.

        """
        game = self.api.search(srcomapi.datatypes.Game, {"name": name})[0]
        return game.id

    def get_game(self, game_id) -> srcomapi.datatypes.Game :
        """Create a game object from the srcomapi module using the game ID from the speedrun.com API.

        Args:
            game_id (str): Game ID retrieved from speedrun.com

        Returns:
            srcomapi.datatypes.Game object from srcomapi.

        """
        return self.api.get_game(game_id)

    def get_category_id(self, game: srcomapi.datatypes.Game, category_name: str) -> str:
        """Get the category ID from a game object by the category's name. 

        Args:
            game (srcomapi.datatypes.Game): A game that has been populated using the srcomapi module.
            category_name (str): The name of a category that belongs to the Game.

        Returns:
            String ID of the categories from speedrun.com. Returns an empty string if no category name matches.

        """
        for category in game.categories:
            if category_name == category.name:
                return str(category.id)
        return ""

    def get_category(self, game: srcomapi.datatypes.Game, category_id: str) -> srcomapi.datatypes.Category:
        """Get the category object from a game object by the category's name.

        Args:
            game (srcomapi.datatypes.Game): A game that has been populated using the srcomapi module.
            category_name (str): The name of a category that belongs to the Game.

        Returns:
            srcomapi.datatypes.Category object from the srcomapi module. Returns None if no category name matches.

        """
        for category in game.categories:
            if category_id == category.id:
                return category
        return None

    def get_level(self, level_id: str) -> srcomapi.datatypes.Level:
        """Get the level object based on the level ID string from speedrun.com API.

        Args:
            level_id (str): The level ID string from speedrun.com API.

        Returns:
            srcomapi.datatypes.Level object from the srcomapi module.

        """
        return srcomapi.datatypes.Level(self.api, data=self.api.get("levels/{}".format(level_id)))

    def get_user(self, user_id: str) -> srcomapi.datatypes.User:
        """Get the user object from the user ID string from speedrun.com API.

        Args:
            user_id (str): The user ID string from speedrun.com API.

        Returns:
            srcomapi.datatypes.User object from srcomapi module.

        """

        return self.api.get_user(user_id)

    def get_leaderboard(self, game_id: str, category_id: str, date: datetime) -> srcomapi.datatypes.Leaderboard:
        """Retrieves a leaderboard object from the srcomapi module. Can optionally retrieve a leaderboard on a given date.

        If the date does not have a valid leaderboard (leaderboard did not
        exist at that date, or some other reason), then it will return the
        leaderboard from the nearest valid date.

        Args:
            game_id (str): A game ID from the speedrun.com API.
            category_id (str): A category ID from the speedrun.com API.
            date (datetime): A datetime object. 

        Returns:
            srcomapi.datatypes.Leaderboard object from srcomapi module.

        """

        return srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables&date={}".format(game_id, category_id, date.isoformat())))

    def get_top_of_leaderboard(self, game_id: str, category_id: str, date: datetime) -> srcomapi.datatypes.Leaderboard:
        """Retrieves the top entry from a leaderboard at a given date.

        If the date does not have a valid leaderboard (leaderboard did not
        exist at that date, or some other reason), then it will return the
        leaderboard from the nearest valid date.

        Args:
            game_id (str): A game ID from the speedrun.com API.
            category_id (str): A category ID from the speedrun.com API.
            date (datetime): A datetime object. 

        Returns:
            srcomapi.datatypes.Leaderboard object from srcomapi module.

        """

        return srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables&top=1&date={}".format(game_id, category_id, date.isoformat())))

    def get_text(self, uri: str):
        """A wrapper around requests.get to safely and robustly get the response body of an external resource.

        Requests are routed through the requests cache for this module. If
        response has a code of 404 or 400, then function exits and returns 0.
        If response is 420 or 504, then we sleep for a time then retry the
        request. If for some reason the response body cannot be returned, we
        try again also.
        
        Args:
            uri (str): The URL that you want to retrieve.

        Returns:
            A string of the response body. If response code is 404 or 400, then we return None.

        """

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
        """A wrapper around requests.get to safely and robustly get the response JSON of an external resource.

        Requests are routed through the requests cache for this module. If
        response has a code of 404 or 400, then function exits and returns 0.
        If response is 420 or 504, then we sleep for a time then retry the
        request. If for some reason the response body cannot be returned, we
        try again also.
        
        Args:
            uri (str): The URL that you want to retrieve.

        Returns:
            A JSON dictionary of the response body. If response code is 404 or 400, then we return None.

        """

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
