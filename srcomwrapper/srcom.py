import srcomapi
from datetime import datetime, timedelta

# TEST_DATE is the end of the time range that we want to scan for. For actual
# purposes this should be datetime.now(). However, for testing it should be
# something closer to release date.
TEST_DATE = datetime(2018, 3, 12)

# API_DEBUG is to print the requests that srcomapi is making.
API_DEBUG = 0

class Srcom:
    """
    Srcom is a personal wrapper over the srcomapi package, and adding
    functionality that will actually be useful for data collection.
    """
    def __init__(self, api_debug=API_DEBUG, date_limit=TEST_DATE):
        self.api = srcomapi.SpeedrunCom()
        self.api.debug = api_debug
        self.date_limit = date_limit

    def games_list(self, name):
        """
        Returns a list of games that are similar to this game as per speedrun.com API.
        """
        return self.api.search(srcomapi.datatypes.Game, {"name": name})

    def single_game(self, name):
        """
        Returns the first game in the list of similar games as per speedrun.com API.
        """
        return self.api.search(srcomapi.datatypes.Game, {"name": name})[0]

    def all_runs_for_all_categories_of_game(self, game_name):
        """
        Returns all the runs for all the categories in a given game. 
        """
        all_runs = {}
        game = self.single_game(game_name)

        # Go through the example on the github to get all runs for all
        # categories of a game.
        for category in game.categories:
            if not category.name in all_runs:
                all_runs[category.name] = {}
            if category.type == 'per-level':
                for level in game.levels:
                  all_runs[category.name][level.name] = srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/level/{}/{}?embed=variables".format(game.id, level.id, category.id)))
            else:
                all_runs[category.name] = srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables".format(game.id, category.id)))

        return all_runs

    def all_runs_for_category_of_game(self, game_name, category_name):
        """
        Returns all the runs for a single category in a given game.
        """
        return self.all_runs_for_all_categories_of_game(game_name)[category_name]

    def all_times_for_runs_in_category_of_game(self, game_name, category_name):
        """
        Returns a list of times (in seconds) of all the runs in a category as
        it is today.
        """
        times = []
        runs = self.all_runs_for_category_of_game(game_name, category_name)
        for run in runs.runs:
            times.append(run['run'].data['times']['primary_t'])
        return sorted(times)

    def category_id_from_name(self, game_name, category_name):
        """
        Returns the internal id of a category in speedun.com
        """
        game = self.single_game(game_name)
        for category in game.categories:
            if category.name == category_name:
               return category.id
        return ""

    def world_record_history_for_category(self, game_name, category_name):
        """
        Returns the time (in seconds) of the top run of a given week since the
        game has been released.
        """
        game = self.single_game(game_name)
        category_id = self.category_id_from_name(game_name, category_name)
        game_date = datetime.strptime(game.data['release-date'], "%Y-%m-%d")
        date_to_record = {}

        # Get the top run from release date until given date, retrieve
        # leaderboard and then increment the date by a week.
        while game_date < self.date_limit:
            leaderboard = srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables&top=1&date={}".format(game.id, category_id, game_date.isoformat())))

            try:
                date_to_record[game_date.isoformat()] = leaderboard.runs[0]['run'].data['times']['primary_t']
            except IndexError:
                # There may not be a top record of the game in the first week,
                # so we can skip this as this doesn't tell us anything.
                pass

            game_date += 7 * timedelta(hours=24)
        return date_to_record

    def players_in_category(self, game_name, category_name):
        """
        Retrieve all unique user ID's of users that have submitted runs
        currently on the leaderboard.
        """
        game = self.single_game(game_name)
        category_id = self.category_id_from_name(game_name, category_name)
        players_in_leaderboard = srcomapi.datatypes.Leaderboard(self.api, data=self.api.get("leaderboards/{}/category/{}?embed=variables,players".format(game.id, category_id))).players["data"]
        game_runners = []
        for player in players_in_leaderboard:
            try:
                game_runners.append(player["id"])
            except KeyError:
                # We get a keyerror if there is a user that submits a run as a
                # guest. If they are a guest they are not submitting multiple
                # runs so won't make much a impact to our analysis.
                pass

        return game_runners 

    def all_runs_for_player(self, player_id):
        """
        Get all the runs that a user has done, including the game, category,
        and place on leaderboard.
        """
        # Not sure why no other data type works, but series works so we're just
        # gonna go with it
        all_player_runs = srcomapi.datatypes.Series(self.api, data=self.api.get("users/{}/personal-bests?embed=variables,game,category".format(player_id)))
        game_category_place = []
        for run in all_player_runs.data:
            game_category_place.append({
                "game": run["game"]["data"]["names"]["international"],
                "category": run["category"]["data"]["name"],
                "place": run["place"],
                })
        return game_category_place 

    def all_other_runs_for_players_in_category(self, game_name, category_name):
        """
        Get other runs for users in a given category.
        """
        all_players_in_category = self.players_in_category(game_name, category_name)
        players_and_runs = [] 
        for player_id in all_players_in_category[:5]:
            player_runs = self.all_runs_for_player(player_id)
            players_and_runs.append({"player_id": player_id, "runs": player_runs})
        return players_and_runs
