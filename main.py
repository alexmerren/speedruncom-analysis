from collector import collector
from os import listdir, rename
from os.path import isfile, join

def main():
    collector.RelatedGamesInformationCollater("all games 10 percent", debug=1).run(percentage_limit=0.1)


if __name__ == "__main__":
    main()
