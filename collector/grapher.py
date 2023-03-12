import csv
import networkx as nx
import graph_tool.all as gt
from graph_tool.centrality import betweenness
from common import generate_network_filter, get_weighted_edges_from_csv

class GraphToolGraph():
    """Class for calculating and saving betweenness centrality values using graph-tool.

    Attributes:
        debug (int): Debug statements enabled with 1, disabled with 0.
        graph (gt.Graph): The generated gt.Graph from the filename.

    Args:
        debug (int): Optional debug statements.

    """

    def __init__(self, debug=0):
        self.debug = debug

    def load_graph_from_csv(self, graph_filename: str, filter_filename: str):
        """Load a graph from a series of CSV files.

        Args:
            graph_filename (str): A CSV file that contains edge pairs.
            filter_filename (str): A CSV file that creates a filter map.

        """

        filter_map = generate_network_filter(filter_filename)
        edges_list = get_weighted_edges_from_csv(graph_filename, filter=filter_map)
        self.graph = gt.Graph(edges_list, hashed=True, hash_type="string", eprops=[('weight', 'double')])

    def load_graph_from_graphml(self, graph_filename: str):
        """Loads a graph from a graphml file.

        Args:
            graph_filename (str): A Graphml filename.

        """

        self.graph = gt.Graph().load(graph_filename)

    def save_graph_to_file(self, filename: str):
        """Save graph to graphml file.

        Args:
            filename (str): File to save graph to.

        """

        self.graph.save(filename)

    def save_betweenness_centrality_to_file(self, filename: str):
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

    def add_betweenness_centrality_to_graph(self, bc_filename: str) -> gt.Graph:
        """Add the betweenness centrality as a property of the graph.

        Args:
            graph (gt.Graph): Graph filled with vertices and edges with optional weights.
            bc_filename (str): The filename of the betweenness centrality of the nodes.

        Returns:
            Graph with the added property of betweenness centrality.

        """

        betweenness_centrality = {}
        with open(bc_filename, 'r', encoding='utf-8') as openfile:
            csv_reader = csv.reader(openfile)
            next(csv_reader)
            for row in csv_reader:
                betweenness_centrality[row[0]] = float(row[1])

        self.graph.vertex_properties["bc"] = self.graph.new_vertex_property("double")

        for vertex in self.graph.vertices():
            name = self.graph.vp.ids[vertex]
            bc = betweenness_centrality[name]
            self.graph.vp.bc[vertex] = bc

        return self.graph 


def main():
    graph = GraphToolGraph(debug=1)
    # graph.load_graph_from_csv("../data/too_big/all_games.csv", "../data/games/metadata/all_games.csv")
    # graph.add_betweenness_centrality_to_graph("../data/games/network_final/all_games_betweenness_centrality.csv")
    # graph.save_graph_to_file("../data/too_big/testgraph.graphml")

    graph.load_graph_from_graphml("../data/too_big/test.graphml")

if __name__ == "__main__":
    main()

