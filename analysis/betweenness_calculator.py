import csv
import networkx as nx
from analysis import common

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
    filter_filename = "../data/games/metadata/all_games.csv"
    filter_map = common.generate_network_filter(filter_filename)

    graph_filename = "../data/too_big/all_games.csv"
    edges_list = get_weighted_edges_from_csv(graph_filename, filter=filter_map)
    graph = generate_graph_from_edges(edges_list)

    print(graph.order(), graph.size())

    betweenness_connectivity_filename = "../data/games/network_final/all_games_betweenness_connectivity.csv"
    find_betweenness_centrality_all_nodes(graph, betweenness_connectivity_filename)

if __name__ == "__main__":
    main()
