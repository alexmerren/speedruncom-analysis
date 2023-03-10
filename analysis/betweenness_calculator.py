import networkx as nx

import csv

from datetime import datetime
from collections import defaultdict

FINAL_DATE = datetime(2023,1,1)

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

def generate_graph_from_edges(edges_list):
    directed_graph = nx.DiGraph()
    directed_graph.add_weighted_edges_from(edges_list)
    return directed_graph

def find_betweenness_centrality_all_nodes(g: nx.Graph, filename: str):
    betweenness_centrality = nx.betweenness_centrality(g, normalized=True, endpoints=True)
    with open(filename, 'w') as openfile:
        openfile.write("id,value\n")
        for node, value in betweenness_centrality.items():
            openfile.write(f"{node},{value}\n")

def main():
    filter_filename = "../data/games_information/all_games.csv"
    filter_map = generate_network_filter(filter_filename)

    graph_filename = "../data/too_big/all_games.csv"
    edges_list = get_weighted_edges_from_csv(graph_filename, filter=filter_map)
    graph = generate_graph_from_edges(edges_list)

    print(graph.order(), graph.size())

    betweenness_connectivity_filename = "../data/too_big/all_games_bc.csv"
    find_betweenness_centrality_all_nodes(graph, betweenness_connectivity_filename)

if __name__ == "__main__":
    main()
