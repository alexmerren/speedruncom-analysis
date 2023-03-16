import csv
import matplotlib

import networkx as nx
import networkx.algorithms.community as nx_comm

from datetime import datetime
from collections import defaultdict

FINAL_DATE = datetime(2023, 1, 1)
REQUEST_TIMEOUT_SLEEP = 2

def generate_network_filter(filename: str, disallowed_games=None) -> dict[str, bool]:
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

            if disallowed_games == None:
                disallowed_games = ["y65797de"]
        
            if created_date < FINAL_DATE and release_date < FINAL_DATE and row[0] not in disallowed_games:
                filter_map[row[0]] = True

    return filter_map

def get_weighted_edges_from_csv(filename: str, filter=None) -> list[tuple[str, str, int]]:
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

def create_nx_graph(graph_filename: str, filter_filename: str):
    filter_map = generate_network_filter(filter_filename)
    edgelist = get_weighted_edges_from_csv(graph_filename, filter_map)
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(edgelist)
    return graph

def find_communities_nx(graph: nx.DiGraph, output_filename: str):
    communities = nx_comm.louvain_communities(graph, seed=0)
    with open(output_filename, 'w', encoding='utf-8') as openfile:
        openfile.write('node_id,community_num\n')
        for community_index, community in enumerate(communities):
            for node_id in community:
                openfile.write(f"{node_id},{community_index}\n")

def main():
    graph = create_nx_graph("../data/too_big/all_games.csv", "../data/games/metadata/all_games.csv")
    find_communities_nx(graph, "../data/games/network/louvain_communities.csv")

if __name__ == "__main__":
    main()

