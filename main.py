from collector import collector,collector_base 
#from datetime import datetime

def main():
    test_name = "super mario odyssey"
    base = collector_base.CollectorBase(debug = 1)

    api = collector.Collector(base, "data/super_mario_odyssey_wr.csv")
    api.record_history_for_game(test_name)

if __name__ == "__main__":
    main()
