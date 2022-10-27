from srcomwrapper.srcom import Srcom
import json

def json_print(thing):
    print(json.dumps(thing))

def main():
    api = Srcom(api_debug=1)

    result = api.all_other_runs_for_players_in_category("super mario odyssey", "Any%")
    print(result)

if __name__ == "__main__":
    main()
