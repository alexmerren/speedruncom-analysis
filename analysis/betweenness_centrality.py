import matplotlib
import networkx as nx
import graph_tool.all as gt
from graph_tool.centrality import betweenness
from common import generate_network_filter, get_weighted_edges_from_csv

class GraphToolGraph():
    def __init__(self, graph_filename: str, filter_filename="../data/games/metadata/all_games.csv"):
        filter_map = generate_network_filter(filter_filename)
        edges_list = get_weighted_edges_from_csv(graph_filename, filter=filter_map)
        self.graph = self.generate_graph_from_edges(edges_list)

    def generate_graph_from_edges(self, edges_list):
        return gt.Graph(edges_list, hashed=True, hash_type="string", eprops=[('weight', 'double')])

    def save_betweenness_centrality(self, filename: str):
        vertex_bc = self.graph.new_vertex_property("double")
        edge_bc = self.graph.new_edge_property("double")
        betweenness(self.graph, vprop=vertex_bc, eprop=edge_bc) 
        
        with open(filename, 'w', encoding='utf-8') as openfile:
            openfile.write("id,value\n")
            for vertex in self.graph.vertices():
                openfile.write(f"{self.graph.vp.ids[vertex]},{vertex_bc[vertex]}\n")

class NetworkXGraph():
    def __init__(self, graph_filename: str, filter_filename="../data/games/metadata/all_games.csv"):
        filter_map = generate_network_filter(filter_filename)
        edges_list = get_weighted_edges_from_csv(graph_filename, filter=filter_map)
        self.graph = self.generate_graph_from_edges(edges_list)

    def generate_graph_from_edges(self, edges_list):
        directed_graph = nx.DiGraph()
        directed_graph.add_weighted_edges_from(edges_list)
        return directed_graph

    def save_betweenness_centrality(self, filename: str):
        betweenness_centrality = nx.betweenness_centrality(self.graph, normalized=True, endpoints=True)
        with open(filename, 'w') as openfile:
            openfile.write("id,value\n")
            for node, value in betweenness_centrality.items():
                openfile.write(f"{node},{value}\n")

def main():
    # NetworkXGraph(graph_filename="../data/too_big/all_games.csv").save_betweenness_centrality(filename="../data/games/network_final/all_games_betweenness_centrality_test.csv")
    GraphToolGraph(graph_filename="../data/too_big/all_games.csv").save_betweenness_centrality(filename="../data/games/network_final/all_games_betweenness_centrality_test.csv")

if __name__ == "__main__":
    main()

