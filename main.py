from collector import collector

def main():
    # data/games_information - 
    collector.GameInformationCollector("updated all games", debug=1).run(start_index=0)

    # data/related_games - all data collection for all games
    # collector.CollatedRelatedGamesCollector("").run(game_start_index=0)

    # data/related_games - spot data collection for missing values
    # collector.IndividualRelatedGamesCollector("smo", debug=1).run(game_id="76r55vd8", user_start_index=1269)
    # collector.IndividualRelatedGamesCollector("supermario64", debug=1).run(game_id="o1y9wo6q")
    # collector.IndividualRelatedGamesCollector("seterra", debug=1).run(game_id="k6q4rqzd")
    # collector.IndividualRelatedGamesCollector("minecraft_java_edition", debug=1).run(game_id="j1npme6p", user_start_index=2774)
    # collector.IndividualRelatedGamesCollector("minecraft_legacy_console_edition", debug=1).run(game_id="yd478gde")
    # collector.IndividualRelatedGamesCollector("superway_surfers", debug=1).run(game_id="y65797de")
    # collector.IndividualRelatedGamesCollector("speed_builders", debug=1).run(game_id="w6jrzxdj")
    # collector.IndividualRelatedGamesCollector("celeste", debug=1).run(game_id="o1y9j9v6")

if __name__ == "__main__":
    main()
