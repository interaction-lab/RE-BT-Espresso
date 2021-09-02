# global imports
import argparse
import os
import pydot
import networkx as nx
import node_helpers as nh
import json
from pathlib import Path


def parse_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--pathtodot", required = True, help = "Path to dot file")
	args = vars(ap.parse_args())

	path_to_dot = None
	if "pathtodot" in args and args["pathtodot"] != None:
		path_to_dot = args["pathtodot"]

	return path_to_dot


def run_result_list(paths):
	results_dict = dict()
	for path in paths:
		run_result(path, results_dict)
	
	# first path in list is simulated
	basename = os.path.basename(paths[0]).replace(".dot", "")
	results_filename = basename + "_results.json" 
	results_path = "./results/"
	write_results(results_path, results_filename, results_dict)

def run_result(path_to_tree_dot_file, results_dict):
	print(f"Start results on generated {path_to_tree_dot_file}")
	graph = nx.nx_pydot.from_pydot(pydot.graph_from_dot_file(path_to_tree_dot_file)[0])
	generate_results(path_to_tree_dot_file, results_dict, graph)


def is_generated(path):
	return "Pruning" in path

# possibly move these out to functions, will leave here for now for convenience
is_generated_key = "is_generated"
num_unique_nodes_key = "num_unique_nodes"
total_nodes_key = "total_nodes" 
unique_node_freq_key = "unique_node_freq"
# assumes key is the full path for `is_generated`
def generate_results(key, results_dict, graph):
	results_dict[key] = dict()
	results_dict[key][is_generated_key] = is_generated(key)
	results_dict[key][num_unique_nodes_key] =  nh.num_unique_nodes(graph)
	results_dict[key][total_nodes_key] = nh.total_num_nodes(graph)
	results_dict[key][unique_node_freq_key] = nh.get_freq_unique_node_dict(graph)
	

def write_results(output_path, results_filename, results_dict):
	results_path = os.path.dirname(output_path) + "/" + results_filename
	Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
	with open(results_path, 'w') as outfile:
		json.dump(results_dict, outfile)
	print(f"Results output to {results_path}")

def main():
	path_to_dot = parse_args()
	run_result(path_to_dot)

if __name__ == '__main__':
	main()
