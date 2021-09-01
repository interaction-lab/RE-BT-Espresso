# global imports
import argparse
import os
import pydot
import networkx as nx
import node_helpers as nh
import json


results_filename = "results.json"
gen_key = "generated"
sim_key = "simulated"
tree_keys = {
	gen_key,
	sim_key
}
num_unique_nodes_key = "num_unique_nodes"
total_nodes_key = "total_nodes"

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
	print(f"Start results on generated {generated_tree_path} from simulated {simulated_tree_path}")
	global gen_key, sim_key, tree_keys, num_unique_nodes
	results_dict = dict()
	graph_dict = dict()
	graph_dict[gen_key] = nx.nx_pydot.from_pydot(pydot.graph_from_dot_file(generated_tree_path)[0])
	graph_dict[sim_key] = nx.nx_pydot.from_pydot(pydot.graph_from_dot_file(simulated_tree_path)[0])

	generate_results(results_dict, graph_dict)
	write_results(simulated_tree_path, results_dict)

def write_results(simulated_tree_path, results_dict):
	results_path = os.path.dirname(simulated_tree_path) + "/" + results_filename
	with open(results_path, 'w') as outfile:
		json.dump(results_dict, outfile)


def generate_results(results_dict, graph_dict):
	for key in tree_keys:
		results_dict[key] = dict()
		results_dict[key][num_unique_nodes_key] =  nh.num_unique_nodes(graph_dict[key])
		results_dict[key][total_nodes_key] = nh.total_num_nodes(graph_dict[key])
			

def main():
	generated_path, simulated_path = parse_args()
	run_result(generated_path, simulated_path)

if __name__ == '__main__':
	main()


# CONVENIENCE COMMAND (used for now before abstarcting out over file system):
#  python3 run_results.py -g ../sim_data/expr0/output/pipeline_output/5_kFold_5_maxDepth/Pruning/Pruning_0_0/behaviortree.dot -s ../sim_data/expr0/expr0.dot