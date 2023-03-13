import csv
from collections import defaultdict

def create_node_to_integer_dict(edgelist_filename: str) -> dict[str, int]:
    nodes = set()
    with open(edgelist_filename, 'r', encoding='utf-8') as openfile:
        csv_reader = csv.reader(openfile)
        next(csv_reader)
        for row in csv_reader:
            nodes.add(row[0])
            nodes.add(row[1])

    node_to_integer_dict = defaultdict(int)
    for index, node in enumerate(nodes):
        node_to_integer_dict[node] = index
    
    return node_to_integer_dict

def format_edgelist(edgelist_filename: str, output_filename: str, node_to_integer_dict: dict[str, int]):
    with open(edgelist_filename, 'r', encoding='utf-8') as readfile:
        csv_reader = csv.reader(readfile)
        next(csv_reader)

        with open(output_filename, 'w', encoding='utf-8') as writefile:
            for row in csv_reader:
                source_int = node_to_integer_dict.get(row[0])
                target_int = node_to_integer_dict.get(row[1])
                weight = float(row[2])
                writefile.write(f"{' '.join(map(str,[source_int,target_int,weight]))}\n")

def main():
    edgelist_filename = "../data/too_big/all_games_filtered.csv"
    node_integer_table = create_node_to_integer_dict(edgelist_filename)
    output_filename = "../data/too_big/all_games_node2vec.edgelist"
    format_edgelist(edgelist_filename, output_filename, node_integer_table)

if __name__ == "__main__":
    main()