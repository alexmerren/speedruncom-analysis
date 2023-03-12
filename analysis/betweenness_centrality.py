import matplotlib
import networkx as nx
import graph_tool.all as gt
from graph_tool.centrality import betweenness
from common import generate_network_filter, get_weighted_edges_from_csv

class GraphToolGraph():
    """Class for calculating and saving betweenness centrality values using graph-tool.

    Attributes:
        debug (int): Debug statements enabled with 1, disabled with 0.
        graph (nx.DiGraph): The generated gt.Graph from the filename.

    Args:
        graph_filename (str): The filename of a list of edges of a graph.
        filter_filename (str): The filename of a list of games that are accepted.
        debug (int): Optional debug statements.

    """

    def __init__(self, graph_filename: str, filter_filename="../data/games/metadata/all_games.csv", debug=0):
        self.debug = debug
        filter_map = generate_network_filter(filter_filename)
        edges_list = get_weighted_edges_from_csv(graph_filename, filter=filter_map)
        self.graph = self.generate_graph_from_edges(edges_list)

    def generate_graph_from_edges(self, edges_list) -> gt.Graph:
        """Creates a gt.Graph from the list of edges.

        Args:
            edges_list (list[tuple[str, str, int]]): A list of edges with weights.

        """

        return gt.Graph(edges_list, hashed=True, hash_type="string", eprops=[('weight', 'double')])

    def save_betweenness_centrality(self, filename: str):
        """Save the betweenness centrality values to a filename.

        Args:
            filename (str): The filename to save to.

        """
        if self.debug >= 1: print(self.graph.get_vertices().shape[0],self.graph.get_edges().shape[0])
        vertex_bc = self.graph.new_vertex_property("double")
        edge_bc = self.graph.new_edge_property("double")
        betweenness(self.graph, vprop=vertex_bc, eprop=edge_bc) 
        
        with open(filename, 'w', encoding='utf-8') as openfile:
            openfile.write("id,value\n")
            for vertex in self.graph.vertices():
                openfile.write(f"{self.graph.vp.ids[vertex]},{vertex_bc[vertex]}\n")

class NetworkXGraph():
    """Class for calculating and saving betweenness centrality values using networkx.

    Attributes:
        debug (int): Debug statements enabled with 1, disabled with 0.
        graph (nx.DiGraph): The generated nx.DiGraph from the filename.

    Args:
        graph_filename (str): The filename of a list of edges of a graph.
        filter_filename (str): The filename of a list of games that are accepted.
        debug (int): Optional debug statements.

    """

    def __init__(self, graph_filename: str, filter_filename="../data/games/metadata/all_games.csv", debug=0):
        self.debug = debug
        filter_map = generate_network_filter(filter_filename)
        edges_list = get_weighted_edges_from_csv(graph_filename, filter=filter_map)
        self.graph = self.generate_graph_from_edges(edges_list)

    def generate_graph_from_edges(self, edges_list: list[tuple[str, str, int]]) -> nx.DiGraph:
        """Creates a nx.DiGraph from the list of edges.

        Args:
            edges_list (list[tuple[str, str, int]]): A list of edges with weights.

        """

        directed_graph = nx.DiGraph()
        directed_graph.add_weighted_edges_from(edges_list)
        return directed_graph

    def save_betweenness_centrality(self, filename: str):
        """Save the betweenness centrality values to a filename.

        Args:
            filename (str): The filename to save to.

        """

        if self.debug >= 1: print(self.graph.order(), self.graph.size())
        betweenness_centrality = nx.betweenness_centrality(self.graph, normalized=True, endpoints=True)
        with open(filename, 'w') as openfile:
            openfile.write("id,value\n")
            for node, value in betweenness_centrality.items():
                openfile.write(f"{node},{value}\n")

def main():
    GraphToolGraph("../data/too_big/all_games.csv", debug=1).save_betweenness_centrality("../data/games/network_final/all_games_betweenness_centrality_test.csv")

if __name__ == "__main__":
    main()

