import csv
import scipy
import random

import networkx as nx
import pandas as pd
import networkx.algorithms.community as nx_comm

from datetime import datetime
from collections import defaultdict
from cdlib import algorithms
from tqdm import tqdm

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

def create_weighted_games_graph(graph_filename: str, filter_filename: str):
    filter_map = generate_network_filter(filter_filename)
    edgelist = get_weighted_edges_from_csv(graph_filename, filter_map)
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(edgelist)
    return graph

def create_games_graph(graph_filename: str, filter_filename: str):
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

def generate_adjacency_matrix(graph: nx.DiGraph):
    return nx.adjacency_matrix(graph, list(graph.nodes()))

def generate_non_existing_edges(graph: nx.DiGraph, adj_graph: scipy.sparse.csr_matrix, node_list: list[str], number_samples: int):
    non_existing_edges = []
    offset = 0
    for i in tqdm(range(adj_graph.shape[0])):
        for j in range(offset, adj_graph.shape[1]):
            if i != j:
                if adj_graph[i, j] == 0:
                    non_existing_edges.extend([(node_list[i], node_list[j])])

        offset += 1
    random_edges = sorted(random.sample(non_existing_edges, k=number_samples))
    return [(i[0],i[1]) for i in tqdm(random_edges) if nx.has_path(graph, i[0], i[1])]

def get_removable_edges(graph: nx.DiGraph):
    number_conected_components = nx.number_weakly_connected_components(graph)
    number_nodes = len(graph.nodes())
    tmp_graph = graph.copy()
    removable_edges = []
    for i in tqdm(list(tmp_graph.edges())[:10000]):
        tmp_graph.remove_edge(*i)

        if nx.number_weakly_connected_components(tmp_graph) == number_conected_components and \
                len(tmp_graph.nodes()) == number_nodes:
            removable_edges.append(i)
            continue

        tmp_graph.add_edge(*i)
    return removable_edges

def generate_removable_edges_data():
    graph = create_games_graph("../data/too_big/all_games.csv", "../data/games/metadata/all_games.csv")
    adj_graph = nx.to_numpy_matrix(graph, nodelist = list(graph.nodes()))
    non_existing_edges = generate_non_existing_edges(graph, adj_graph, list(graph.nodes()), 4000)
    non_existing_edges_df = pd.DataFrame(data=non_existing_edges, columns=['source', 'target'])
    non_existing_edges_df['connection'] = 0
    removable_edges = get_removable_edges(graph)
    removable_edges_df = pd.DataFrame(data=removable_edges, columns=['source', 'target'])
    removable_edges_df['connection'] = 1
    dataset = non_existing_edges_df.append(removable_edges_df, ignore_index=True)
    dataset.to_csv('../data/games/network/edge_existence_dataset.csv')

def format_user_preferences_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df[(df['signup_date'].notna()) & (df['signup_date'] != "Null")]
    df['signup_date'] = pd.to_datetime(df['signup_date'], format='%Y-%m-%dT%H:%M:%SZ')
    df['signup_date'] = pd.to_datetime(df['signup_date'].dt.strftime('%Y-%m-%d'))
    df = df[(df['signup_date'] < '2023-01-01')]
    return df

def explode_user_preferences_df(df: pd.DataFrame) -> pd.DataFrame:
    exploded_games_df = df.copy()
    exploded_games_df['games'] = exploded_games_df['games'].str.split(',')
    exploded_games_df = exploded_games_df.explode('games').rename(columns = {'games': 'game_id', 'user':'user_id'})[['user_id', 'game_id']]
    return exploded_games_df

def create_bipartite_user_graph(df: pd.DataFrame) -> nx.Graph:
    bipartite_graph = nx.Graph()
    bipartite_graph.add_nodes_from(set(df['user_id'].values), bipartite=0)
    bipartite_graph.add_nodes_from(set(df['game_id'].values), bipartite=1)
    bipartite_graph.add_edges_from([(user, game) for user, game in zip(df['user_id'], df['game_id'])])
    assert nx.is_bipartite(bipartite_graph)
    return bipartite_graph

def generate_communities_for_bipartite_user_graph():
    user_prefs_df = pd.read_csv("../data/users/user_preferences_with_metadata.csv")
    user_prefs_df = format_user_preferences_df(user_prefs_df)
    user_prefs_df = explode_user_preferences_df(user_prefs_df)
    bipartite_graph = create_bipartite_user_graph(user_prefs_df)
    #find_louvain_communities(bipartite_graph, "../data/users/louvain_communities.csv")
    find_greedy_modularity_communities(bipartite_graph, "../data/users/greedy_modularity_communities.csv")
    find_infomap_communities(bipartite_graph, "../data/users/infomap_communities.csv")

def main():
    generate_communities_for_bipartite_user_graph()

if __name__ == "__main__":
    main()

