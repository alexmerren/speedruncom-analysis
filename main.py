from collector import collector

def main():
    collector.RelatedGamesCollector().run(game_start_index=21_000, player_start_index=0)

if __name__ == "__main__":
    main()
