from collector import collector

def main():
    # The name field is blank as this API does not write to disk, it creates writeApis internally.
    collector.CollatedWorldRecordHistoryCollector("", debug=1).run(game_start_index=30850)
    # collector.RelatedGamesCollector("all games 10 percent", debug=1).run(percentage_limit=0.1)

if __name__ == "__main__":
    main()
