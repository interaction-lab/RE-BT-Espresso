# global imports
import argparse
import sys, os
import glob
import pydot
import networkx as nx
import node_helpers as nh

def parse_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-g", "--generated", required = True, help = "Path to generated tree")
	ap.add_argument("-s", "--simulated", required = True, help = "Path to simulated tree")
	args = vars(ap.parse_args())

	generated_path = simulated_path = None
	if "generated" in args and args["generated"] != None:
		generated_path = args["generated"]
	if "simulated" in args and args["simulated"] != None:
		simulated_path = args["simulated"]

	return generated_path, simulated_path




def run_result(generated_tree_path, simulated_tree_path):
	print(f"Start results on {generated_tree_path}")
	generated_graph = nx.nx_pydot.from_pydot(pydot.graph_from_dot_file(generated_tree_path)[0])
	simulated_graph = nx.nx_pydot.from_pydot(pydot.graph_from_dot_file(simulated_tree_path)[0])
	print(nh.num_unique_nodes(generated_graph))
	print(nh.num_unique_nodes(simulated_graph))


def main():
	generated_path, simulated_path = parse_args()
	run_result(generated_path, simulated_path)

if __name__ == '__main__':
	main()


# CONVENIENCE COMMAND (used for now before abstarcting out over file system):
#  python3 run_results.py -g ../sim_data/expr0/output/pipeline_output/5_kFold_5_maxDepth/Pruning/Pruning_0_0/behaviortree.dot -s ../sim_data/expr0/expr0.dot