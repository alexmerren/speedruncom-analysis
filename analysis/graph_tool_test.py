import csv
import matplotlib
import numpy as np
import graph_tool.all as gt
from graph_tool.centrality import betweenness
from collections import defaultdict
from datetime import datetime
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
    return gt.Graph(edges_list, hashed=True, hash_type="string", eprops=[('weight', 'double')])

def create_filtered_graph_from_csv(filename: str):
    filter_filename = "../data/games/metadata/all_games.csv"
    filter_map = common.generate_network_filter(filter_filename)
    edges = get_weighted_edges_from_csv(filename, filter=filter_map)
    return generate_graph_from_edges(edges)

def draw_graph_with_vp_ep(graph, vp, ep):
    gt.graph_draw(graph, vertex_fill_color=vp,
               vertex_size=prop_to_size(vp, mi=5, ma=15),
               edge_pen_width=prop_to_size(ep, mi=0.5, ma=5),
               vcmap=matplotlib.cm.gist_heat,
               vorder=vp, output="test.pdf")

def main():
    graph_filename = "../data/too_big/all_games.csv"
    graph = create_filtered_graph_from_csv(graph_filename)
    vertex_bc = graph.new_vertex_property("double")
    edge_bc = graph.new_edge_property("double")
    betweenness(graph, vprop=vertex_bc, eprop=edge_bc) 

    print(f"edges: {len(edge_bc.a)}")

    filename = "../data/too_big/all_games_betweenness_centrality.csv"
    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("id,value\n")
        for vertex in graph.vertices():
            openfile.write(f"{graph.vp.ids[vertex]},{vertex_bc[vertex]}\n")

if __name__ == "__main__":
    main()

