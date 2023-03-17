import csv
import matplotlib

import networkx as nx
import networkx.algorithms.community as nx_comm

from datetime import datetime
from collections import defaultdict
from cdlib import algorithms

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


def get_edges_from_csv(filename: str, filter=None) -> list[tuple[str, str]]:
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
                edges.append(tuple([row[0], row[1]]))
                continue

            if not filter.get(row[0]) or not filter.get(row[1]):
                continue

            edges.append(tuple([row[0], row[1]]))

    return edges

def create_weighted_graph(graph_filename: str, filter_filename: str):
    filter_map = generate_network_filter(filter_filename)
    edgelist = get_weighted_edges_from_csv(graph_filename, filter_map)
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(edgelist)
    return graph

def create_graph(graph_filename: str, filter_filename: str):
    filter_map = generate_network_filter(filter_filename)
    edgelist = get_edges_from_csv(graph_filename, filter_map)
    graph = nx.DiGraph()
    graph.add_edges_from(edgelist)
    return graph

def find_infomap_communities(graph: nx.DiGraph, output_filename: str):
    communities = algorithms.infomap(graph).communities
    with open(output_filename, 'w', encoding='utf-8') as openfile:
        openfile.write('node_id,community_num\n')
        for community_index, community in enumerate(communities):
            for node_id in community:
                openfile.write(f"{node_id},{community_index}\n")

def find_louvain_communities(graph: nx.DiGraph, output_filename: str):
    communities = nx_comm.louvain_communities(graph, seed=0)
    with open(output_filename, 'w', encoding='utf-8') as openfile:
        openfile.write('node_id,community_num\n')
        for community_index, community in enumerate(communities):
            for node_id in community:
                openfile.write(f"{node_id},{community_index}\n")

def find_greedy_modularity_communities(graph: nx.DiGraph, output_filename: str):
    communities = nx_comm.greedy_modularity_communities(graph)
    with open(output_filename, 'w', encoding='utf-8') as openfile:
        openfile.write('node_id,community_num\n')
        for community_index, community in enumerate(communities):
            for node_id in community:
                openfile.write(f"{node_id},{community_index}\n")

def create_node_to_cluster_map(communities_filename: str) -> dict[str, int]:
    with open(communities_filename, 'r', encoding='utf-8') as openfile:
        csv_reader = csv.reader(openfile)
        next(csv_reader)
        node_to_cluster = defaultdict(int)
        for row in csv_reader:
            node_to_cluster[row[0]] = int(row[1])
    return node_to_cluster


def save_weighted_graph(g: nx.DiGraph, filename: str):
    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("Source,Target,Weight\n")
        for source,target,data in g.edges(data=True):
            weight = int(data['weight'])
            output_string = ','.join(map(str, [source, target, weight]))
            openfile.write(f"{output_string}\n")

def create_meta_graph(graph: nx.DiGraph, node_to_cluster_map: dict[str, int]) -> nx.DiGraph:
    source_target_number = defaultdict(int)
    for source, target in graph.edges():
        key = str(node_to_cluster_map[source]) + ' ' + str(node_to_cluster_map[target])
        source_target_number[key] += 1
    
    meta_graph = nx.DiGraph()
    for connection, weight in source_target_number.items():
        split_connection = connection.split(' ')
        source = split_connection[0]
        target = split_connection[1]
        if source == target:
            continue
        meta_graph.add_edge(source, target, weight=weight)
        
    return meta_graph

def main():
    graph = create_graph("../data/too_big/all_games.csv", "../data/games/metadata/all_games.csv")
    find_louvain_communities(graph, "../data/games/network/louvain_noweight_communities.csv")
    find_greedy_modularity_communities(graph, "../data/games/network/greedy_modular_noweight_communities.csv")
    find_infomap_communities(graph, "../data/games/network/infomap_noweight_communities.csv")

if __name__ == "__main__":
    main()

