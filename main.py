from collector import collector

def main():
    collector.GameInformationCollector("updated all games", debug=1).run(start_index=32670)

if __name__ == "__main__":
    main()
