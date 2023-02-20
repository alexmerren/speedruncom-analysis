from collector import collector

def main():
    # data/games_information - 
    #collector.GameInformationCollector("updated all games", debug=1).run(start_index=0)

    # data/related_games - all data collection for all games
    # collector.CollatedRelatedGamesCollector("").run(game_start_index=0)

    # data/related_games - spot data collection for missing values
    collector.IndividualRelatedGamesCollector("subway_surfers", debug=1).run(game_id="y65797de")

if __name__ == "__main__":
    main()
