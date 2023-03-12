import csv
import matplotlib
import graph_tool.all as gt
from graph_tool.centrality import betweenness
from common import generate_network_filter, get_weighted_edges_from_csv

def load_graph_from_csv(graph_filename: str, filter_filename: str):
    """Load a graph from a series of CSV files.

    Args:
        graph_filename (str): A CSV file that contains edge pairs.
        filter_filename (str): A CSV file that creates a filter map.

    """

    filter_map = generate_network_filter(filter_filename)
    edges_list = get_weighted_edges_from_csv(graph_filename, filter=filter_map)
    return gt.Graph(edges_list, hashed=True, hash_type="string", eprops=[('weight', 'double')])

def save_graph_to_file(graph: gt.Graph, filename: str):
    """Save graph to graphml file.

    Args:
        filename (str): File to save graph to.

    """

    graph.save(filename)

def save_betweenness_centrality_to_file(graph: gt.Graph, filename: str):
    """Save the betweenness centrality values to a filename.

    Args:
        filename (str): The filename to save to.

    """
    print(graph.get_vertices().shape[0],graph.get_edges().shape[0])
    vertex_bc = graph.new_vertex_property("double")
    edge_bc = graph.new_edge_property("double")
    betweenness(graph, vprop=vertex_bc, eprop=edge_bc) 
    
    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("id,value\n")
        for vertex in graph.vertices():
            openfile.write(f"{graph.vp.ids[vertex]},{vertex_bc[vertex]}\n")

def add_betweenness_centrality_to_graph(graph: gt.Graph, bc_filename: str) -> gt.Graph:
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

    graph.vertex_properties["bc"] = graph.new_vertex_property("double")

    for vertex in graph.vertices():
        name = graph.vp.ids[vertex]
        bc = betweenness_centrality[name]
        graph.vp.bc[vertex] = bc

    return graph 

def visualise_graph(graph: gt.Graph):
    position = gt.sfdp_layout(graph)
    gt.graph_draw(graph, pos=position, vertex_fill_color=graph.vp.bc,
               vertex_size=gt.prop_to_size(graph.vp.bc, mi=5, ma=15),
               vcmap=matplotlib.cm.gist_heat,
               vorder=graph.vp.bc, output="test.pdf")

def main():
    # This is how we load from a CSV file and save to a graphml file.
    # graph = load_graph_from_csv("../data/too_big/all_games.csv", "../data/games/metadata/all_games.csv")
    # graph = add_betweenness_centrality_to_graph(graph, "../data/games/network_final/all_games_betweenness_centrality.csv")
    # save_graph_to_file(graph, "../data/too_big/testgraph.graphml")

    graph = gt.load_graph("../data/too_big/test.graphml")
    visualise_graph(graph)

if __name__ == "__main__":
    main()

