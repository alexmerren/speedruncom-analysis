from collector import collector

def main():
    collector.RelatedGamesInformationCollater("all games filtered", debug=1).run(percentage_limit=1)
    collector.RelatedGamesInformationCollater("all games", debug=1).run(percentage_limit=1, doFilter=False)

if __name__ == "__main__":
    main()
