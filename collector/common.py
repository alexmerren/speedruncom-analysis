import csv
import requests
import time
from datetime import datetime
from collections import defaultdict
from requests_cache import CachedSession

FINAL_DATE = datetime(2023, 1, 1)
REQUEST_TIMEOUT_SLEEP = 2

REQUEST_CACHE_NAME = "user_preference_cache"
REQUEST_TIMEOUT_SLEEP = 2

requests_c = CachedSession(
        REQUEST_CACHE_NAME, 
        backend='sqlite',
        expire_after=None)

def generate_network_filter(filename: str) -> dict[str, bool]:
    """Create a dictionary containing the games that we want to include in further analysis.
    
    We check if a game was released/created before the cutoff date, and if the
    game is in a disallowed games list. If the answer to both of these
    questions is no, then we want to include it in our analysis.

    Args:
        filename (str): The name of the games metadata file.

    Returns:
        A dictionary of game ID to boolean. If the game is allowed True, if not False.

    """

    with open(filename, 'r', encoding='utf-8') as openfile:
        csv_reader = csv.reader(openfile)
        next(csv_reader)
        filter_map = defaultdict(bool)
        for row in csv_reader:
            # Check if the created/release date is after 2023, if it is then we can ignore it in the network.
            release_date = datetime.strptime(row[3], "%Y-%m-%d")
            if row[4] == "None":
                row[4] = "2017-10-22T05:21:29Z" # This is a completely random date before the final date.
            created_date = datetime.strptime(row[4], "%Y-%m-%dT%H:%M:%SZ")

            disallowed_games = ["y65797de"]

            if created_date < FINAL_DATE and release_date < FINAL_DATE and \
                row[0] not in disallowed_games and row[1] not in disallowed_games:
                filter_map[row[0]] = True

    return filter_map

def get_weighted_edges_from_csv(filename, filter=None) -> list[tuple[str, str, int]]:
    """Create a list of edges with structure `node1,node2,weight`.

    Args:
        filename (str): The filename containing a list of edges.
        filter (dict[str, bool]): The filter of which games to allow.

    Returns:
        A list of tuples of edges and their weights.

    """

    with open(filename, 'r', encoding='utf-8') as openfile:
        csv_reader = csv.reader(openfile)
        next(csv_reader)

        edges = list()
        for row in csv_reader:
            if filter is None:
                edges.append(tuple([row[0], row[1], int(row[2])]))
                continue
            
            if not filter.get(row[0]) or not filter.get(row[1]):
                continue

            edges.append(tuple([row[0], row[1], int(row[2])]))

    return edges

def get(uri: str):
    """Get request a URI.

    Run requests through a requests cache defined above. If response code is
    404 or 400, then return None. If response code is 420 or 504, then retry
    after timeout.

    Args:
        uri (str): The URL of a resource.

    Returns:
        JSON of a response body.

    """

    print(uri)
    response = requests_c.get(uri)
    if response.status_code in [404,400]:
        print(f"({response.status_code}) {response.reason}: Exiting. {response.json()=}")
        return None
    if response.status_code in [420,504]:
        print(f"({response.status_code}) {response.reason}: re-requesting.")
        time.sleep(REQUEST_TIMEOUT_SLEEP)
        return get(uri)
    try:
        return response.json()
    except: 
        print(f"({response.status_code}) {response.reason}: re-requesting")
        time.sleep(REQUEST_TIMEOUT_SLEEP)
        return get(uri)
