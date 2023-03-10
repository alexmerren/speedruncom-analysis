from collector import collector

def main():
    # collector.RelatedGamesInformationCollater("games network 10 percent", debug=1).run(percentage_limit=0.1)
    # collector.RelatedGamesInformationCollater("games network full", debug=1).run(percentage_limit=1)

    # Spot collection attempt for subway surfers, it still 5XX's.
    # collector.GameInformationCollector("test", debug=1).run(start_index=16402)

if __name__ == "__main__":
    main()
