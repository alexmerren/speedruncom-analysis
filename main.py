from collector import collector

def main():
    # collector.RelatedGamesInformationCollater("all games 10 percent", debug=1).run(percentage_limit=0.1)
    # collector.RelatedGamesInformationCollater("all games 20 percent", debug=1).run(percentage_limit=0.2)
    # collector.RelatedGamesInformationCollater("all games 30 percent", debug=1).run(percentage_limit=0.3)
    # collector.RelatedGamesInformationCollater("all games 40 percent", debug=1).run(percentage_limit=0.4)
    # collector.RelatedGamesInformationCollater("all games 50 percent", debug=1).run(percentage_limit=0.5)
    # collector.RelatedGamesInformationCollater("all games 60 percent", debug=1).run(percentage_limit=0.6)
    # collector.RelatedGamesInformationCollater("all games 70 percent", debug=1).run(percentage_limit=0.7)
    # collector.RelatedGamesInformationCollater("all games 80 percent", debug=1).run(percentage_limit=0.8)
    # collector.RelatedGamesInformationCollater("all games 90 percent", debug=1).run(percentage_limit=0.9)
    # collector.RelatedGamesInformationCollater("all games", debug=1).run(percentage_limit=1)

    collector.GameInformationCollector("test", debug=1).run(start_index=16402)

if __name__ == "__main__":
    main()
