import csv
import requests
import time
from datetime import datetime
from collections import defaultdict

FINAL_DATE = datetime(2023, 1, 1)
REQUEST_TIMEOUT_SLEEP = 2

def generate_network_filter(filename: str):
    with open(filename, 'r') as openfile:
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

def get_weighted_edges_from_csv(filename, filter=None):
    with open(filename, 'r') as openfile:
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
    print(uri)
    response = requests.get(uri)
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