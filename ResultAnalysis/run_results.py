# global imports
import argparse
import sys, os
import glob
import pydot
import networkx as nx
import node_helpers as nh
import numpy as np
import re

def parse_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-g", "--generated", required = True, help = "Path to generated tree")
	args = vars(ap.parse_args())
	generated_path = None
	if "generated" in args and args["generated"] != None:
		generated_path = args["generated"]

	return generated_path


def get_freq_unique_node_dict(graph):
	freq_dict = nh.unique_node_freq_counter()
	node_regex = nh.get_node_regex_dict()
	for node in graph.nodes:
		for reg_pat, node_type in node_regex.items():
			if reg_pat == "*" or re.search(reg_pat, node):
				freq_dict[node_type] += 1
				continue # go to next node
	return freq_dict

def num_unique_nodes(graph):
	print(get_freq_unique_node_dict(graph))
	print(get_freq_unique_node_dict(graph).values())
	return np.count_nonzero(get_freq_unique_node_dict(graph).values())

def run_result(generated_tree_path):
	print(f"Start results on {generated_tree_path}")
	graph = nx.nx_pydot.from_pydot(pydot.graph_from_dot_file(generated_tree_path)[0])
	print(graph.nodes)
	print(graph.edges)
	print(num_unique_nodes(graph))


def main():
	generated_path = parse_args()
	run_result(generated_path)

if __name__ == '__main__':
	main()
