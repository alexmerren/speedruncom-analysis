import csv
import matplotlib

import graph_tool.all as gt

from graph_tool.centrality import betweenness
from datetime import datetime
from collections import defaultdict

FINAL_DATE = datetime(2023, 1, 1)
REQUEST_TIMEOUT_SLEEP = 2

def generate_network_filter(filename: str) -> dict[str, bool]:
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

            disallowed_games = ["y65797de"]

            if created_date < FINAL_DATE and release_date < FINAL_DATE and \
                row[0] not in disallowed_games and row[1] not in disallowed_games:
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

def load_graph_from_csv(graph_filename: str, filter_filename: str) -> gt.Graph:
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
        graph (gt.Graph): The graph to calculate the betweenness centrality of.
        filename (str): The filename to save to.

    """

    print(graph.get_vertices().shape[0],graph.get_edges().shape[0])
    vertex_bc = graph.new_vertex_property("double")
    betweenness(graph, vprop=vertex_bc, weight=graph.ep.weight) 
    
    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("id,value\n")
        for vertex in graph.vertices():
            openfile.write(f"{graph.vp.ids[vertex]},{vertex_bc[vertex]}\n")

def save_closeness_centrality_to_file(graph: gt.Graph, filename: str):
    print(graph.get_vertices().shape[0], graph.get_edges().shape[0])
    vertex_closeness = graph.new_vertex_property("double")
    closeness(graph, vprop=vertex_closeness, weight=graph.ep.weight)

    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("id,value\n")
        for vertex in graph.vertices():
            openfile.write(
                f"{graph.vp.ids[vertex]},{vertex_closeness[vertex]}\n")

def save_eigenvector_centrality_to_file(graph: gt.Graph, filename: str) -> float:
    """Saves the eigenvector centrality of a graph to a file. 

    Args:
        graph (gt.Graph): The graph.
        filename (str): The filename to save to.
    
    Returns:
        A float of the largest eigenvalue in the graph.
        
    """

    print(graph.get_vertices().shape[0], graph.get_edges().shape[0])
    vertex_eigenvector = graph.new_vertex_property("double")
    eigenvalue, _ = eigenvector(graph, vprop=vertex_eigenvector, weight=graph.ep.weight)

    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("id,value\n")
        for vertex in graph.vertices():
            openfile.write(
                f"{graph.vp.ids[vertex]},{vertex_eigenvector[vertex]}\n")
            
    return eigenvalue

def save_hits_centrality_to_file(graph: gt.Graph, filename: str):
    """Calculates hits centrality and writes to a given file.

    Args:
        graph (gt.Graph): A graph to calculate the hits centrality.
        filename (str): A filename to store the authority and hub values for all vertices.
    """

    print(graph.get_vertices().shape[0], graph.get_edges().shape[0])
    authority_centrality = graph.new_vertex_property("double")
    hub_centrality = graph.new_vertex_property("double")
    hits(graph, xprop=authority_centrality, yprop=hub_centrality, weight=graph.ep.weight)

    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("id,authority_value,hub_value\n")
        for vertex in graph.vertices():
            openfile.write(
                f"{graph.vp.ids[vertex]},{authority_centrality[vertex]},{hub_centrality[vertex]}\n")

def save_pagerank_to_file(graph: gt.Graph, filename: str):
    """Saves the pagerank values of a graph to a file. 

    Args:
        graph (gt.Graph): The graph.
        filename (str): The filename to save to.
        
    """

    print(graph.get_vertices().shape[0], graph.get_edges().shape[0])
    vertex_pagerank = graph.new_vertex_property("double")
    pagerank(graph, vprop=vertex_pagerank, weight=graph.ep.weight)

    with open(filename, 'w', encoding='utf-8') as openfile:
        openfile.write("id,value\n")
        for vertex in graph.vertices():
            openfile.write(
                f"{graph.vp.ids[vertex]},{vertex_pagerank[vertex]}\n")

def add_property_to_graph_from_file(graph: gt.Graph, property_name: str, filename: str) -> gt.Graph:
    """Add a property to a graph using a CSV file of node IDs to values.

    Args:
        graph (gt.Graph): Graph filled with vertices and edges with optional weights.
        property_name (str): The name of the property added.
        bc_filename (str): The filename of the properties of the nodes.

    Returns:
        Graph with the added property.

    """

    property_map  = {}
    with open(filename, 'r', encoding='utf-8') as openfile:
        csv_reader = csv.reader(openfile)
        next(csv_reader)
        for row in csv_reader:
            property_map[row[0]] = float(row[1])

    graph.vertex_properties[property_name] = graph.new_vertex_property("double")

    for vertex in graph.vertices():
        name = graph.vp.ids[vertex]
        prop = property_map[name]
        graph.vp[property_name][vertex] = prop

    return graph 

def visualise_graph(graph: gt.Graph):
    position = gt.sfdp_layout(graph)
    gt.graph_draw(graph, pos=position, vertex_fill_color=graph.vp.prop,
               vertex_size=gt.prop_to_size(graph.vp.prop, mi=5, ma=15),
               vcmap=matplotlib.cm.gist_heat,
               vorder=graph.vp.prop, output="test.pdf")

def main():
    # This is how we load from a CSV file and save to a graphml file.
    # graph = load_graph_from_csv("../data/too_big/all_games.csv", "../data/games/metadata/all_games.csv")
    # graph = add_property_to_graph_from_file(graph, "../data/games/network_final/all_games_betweenness_centrality.csv")
    # save_graph_to_file(graph, "../data/too_big/testgraph.graphml")
    # print(graph.get_vertices().shape[0],graph.get_edges().shape[0])

    graph = load_graph_from_csv("../data/too_big/all_games.csv", "../data/games/metadata/all_games.csv")
    save_pagerank_to_file(graph, "../data/games/network_final/all_games_pagerank.csv")
    save_hits_centrality_to_file(graph, "../data/games/network_final/all_games_hits_centrality.csv")
    save_closeness_centrality_to_file(graph, "../data/games/network_final/all_games_closeness_centrality.csv")


if __name__ == "__main__":
    main()

