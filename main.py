from collector import collector

def main():
    collector.RelatedGamesInformationCollater("all games filtered", debug=1).run()
    collector.RelatedGamesInformationCollater("all games", debug=1).run(doFilter=False)

if __name__ == "__main__":
    main()
