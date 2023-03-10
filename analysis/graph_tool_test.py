import csv

import matplotlib

from graph_tool.all import *
from graph_tool.centrality import betweenness

from collections import defaultdict
from datetime import datetime

FINAL_DATE = datetime(2023, 1, 1)


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
    directed_graph = Graph()
    directed_graph.add_edge_list(edges_list, hashed=True, hash_type="string")
    graph_view = GraphView(directed_graph, vfilt=label_largest_component(directed_graph))
    return graph_view

def create_filtered_graph_from_csv(filename: str):
    filter_filename = "../data/games/metadata/all_games.csv"
    filter_map = generate_network_filter(filter_filename)
    edges = get_weighted_edges_from_csv(filename, filter=filter_map)
    return generate_graph_from_edges(edges)

def main():
    graph_filename = "../data/too_big/all_games.csv"
    graph = create_filtered_graph_from_csv(graph_filename)
    vp, ep = betweenness(graph) 
    print(f"Number of Edges: {len(ep.a)}")
    graph_draw(graph, vertex_fill_color=vp,
               vertex_size=prop_to_size(vp, mi=5, ma=15),
               edge_pen_width=prop_to_size(ep, mi=0.5, ma=5),
               vcmap=matplotlib.cm.gist_heat,
               vorder=vp, output="test.pdf")

if __name__ == "__main__":
    main()

