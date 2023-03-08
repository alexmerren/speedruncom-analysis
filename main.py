from collector import collector
from os import listdir, rename
from os.path import isfile, join

def main():
    path = "data/related_games/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    invalid_chars = ["<", ">", ":", "\"", "?", "|", "?", "*"]
    for filename in files:
        if any(char in filename for char in invalid_chars):
            print(filename)


if __name__ == "__main__":
    main()
