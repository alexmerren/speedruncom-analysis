import csv

import networkx as nx

from networkx.algorithms import community, pagerank

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

def find_most_popular_in_graph_pagerank(g: nx.Graph) -> tuple[str, float]:
    values = pagerank(g)
    return max(values.items(), key=lambda x: x[1])

def main():
    filename = "../data/too_big/all_related_games.csv"
    # filename = "../data/too_big/all_related_games_10_percent.csv"
    edges = get_weighted_edges_from_csv(filename)
    graph = generate_graph_from_edges(edges)
    # N, K = graph.order(), graph.size()
    # avg_deg = float(K) / N
    # print(f"{N=},{K=},{avg_deg=}")

if __name__ == "__main__":
    main()
