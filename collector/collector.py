from . import collector_base 

from datetime import timedelta, datetime

FINAL_DATE = datetime(2023, 1, 1)

class Collector:
    def __init__(self, base: collector_base.CollectorBase, filename: str) -> None:
        self.base = base
        self.filename = filename

    def record_history_for_game(self, game_name: str, start_date=None, end_date=FINAL_DATE) -> None:
        game_id = self.base.get_game_id(game_name)
        game = self.base.get_game(game_id)
        category_list = game.categories[2:]

        # If a start date is not specified, we go from when the game was released.
        if start_date == None:
            start_date = datetime.strptime(game.data['release-date'], "%Y-%m-%d")

        with open(self.filename, 'a') as openfile:
            openfile.write("game_name,game_id,category_name,category_id,date,user_id,run_id,time\n")

            for category in category_list:
                # Add a week from the release date to allow a run to be on the board.
                current_date = start_date + timedelta(weeks=1)

                while current_date < end_date:
                    run_data = self.base.get_top_of_leaderboard(game_id, category.id, current_date).data

                    try:
                       run_data = run_data["runs"][0]["run"]
                    except IndexError:
                        # We only encounter this error if there are no records on the given date.
                        # This happens if the category hasn't been invented on the date we select.
                        current_date += timedelta(weeks=1)
                        continue

                    run_id = run_data["id"]
                    time = run_data["times"]["primary_t"]
                    users = run_data["players"]

                    for user in users :
                        user_id = user.get("name") if user.get("id") is None else user.get("id")
                        openfile.write(f"{game_name},{game_id},{category.name},{category.id},{current_date.isoformat()},{user_id},{run_id},{time}\n")

                    current_date += timedelta(weeks=1)


    def related_games_from_game(self, game_name: str):
        pass
