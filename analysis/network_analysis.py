import csv

import networkx as nx

from networkx.algorithms import pagerank

def get_weighted_edges_from_csv(filename: str):
    with open(filename, 'r') as openfile:
        csv_reader = csv.reader(openfile)
        next(csv_reader)
        edges = [tuple([row[0], row[1], int(row[2])]) for row in csv_reader]

    return edges

def generate_graph_from_edges(edges_list):
    directed_graph = nx.DiGraph()
    directed_graph.add_weighted_edges_from(edges_list)
    return directed_graph

def find_top_n_pagerank_nodes(g: nx.Graph, n=1):
    values = pagerank(g)
    values_sorted = dict(sorted(values.items(), key=lambda item: item[1], reverse=True))
    return list(values_sorted)[0:n]

def get_graph_order_size(g: nx.Graph):
    return g.order(), g.size()

def find_top_n_betweenness_centrality_nodes(g: nx.Graph, n=10):
    degree_centrality = nx.degree_centrality(g)
    betweenness_centrality = nx.betweenness_centrality(g, normalized=True, endpoints=True)

    degree_centrality_sorted = dict(sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True))
    betweenness_centrality_sorted = dict(sorted(betweenness_centrality.items(), key=lambda item: item[1], reverse=True))

    keys_top_degree = list(degree_centrality_sorted)[0:n]
    keys_top_betweenness = list(betweenness_centrality_sorted)[0:n]
    return list(set(keys_top_degree) & set(keys_top_betweenness))

def main():
    # filename = "../data/too_big/all_related_games.csv"
    filename = "../data/too_big/all_games_10_percent.csv"
    edges = get_weighted_edges_from_csv(filename)
    graph = generate_graph_from_edges(edges)
    print(get_graph_order_size(graph))
    print(find_top_n_betweenness_centrality_nodes(graph, n=100))

if __name__ == "__main__":
    main()
