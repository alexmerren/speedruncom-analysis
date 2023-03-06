from collector import collector

def main():
    # The name field is blank as this API does not write to disk, it creates writeApis internally.
    collector.CollatedWorldRecordHistoryCollector("", debug=1).run(game_start_index=28614)

if __name__ == "__main__":
    main()
