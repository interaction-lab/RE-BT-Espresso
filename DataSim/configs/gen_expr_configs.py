import random
import json
import os
from pathlib import Path
import pprint
import copy

max_sub_trees = 3

num_actions = 5
action_set = ["action_" + str(i) for i in range(num_actions)]
num_conditions = 5
target_state_set = ["env_state_var_" + str(i) for i in range(num_conditions)]

root_set = ["parallel", "selector", "sequence"]
composite_set = ["parallel", "selector", "sequence", "repeat", "parsel"]
leaf_set = ["condition"]

default_entry = {
	"name" : "DEFAULT",
	"type_" : "DEFAULT",
	"p_success" : 1,
	"inverted" : False,
	"threshold" : 0.5
}

default_w_child = copy.deepcopy(default_entry)
default_w_child["child_list"] = []

output_path = "./experiments"

total_num_experiments = 100
expr_num = range(5, total_num_experiments)


def get_root_type():
	global root_set
	return random.sample(root_set, 1)

def choose_composite_type():
	global composite_set
	return random.sample(composite_set, 1)

def choose_random_action():
	global action_set
	return random.sample(action_set, 1)

def create_leaf(leaf_entry):
	leaf_entry["type_"] = "action"
	leaf_entry["name"] = choose_random_action()

def create_composite_node(composite_entry):
	global default_entry
	my_entry = copy.deepcopy(default_entry)
	create_leaf(my_entry)
	composite_entry["child_list"].append(my_entry)

def gen_subtree(tree_dict):
	# compositechoice
	composite_entry = copy.deepcopy(default_w_child)
	composite_entry["type_"] = choose_composite_type()
	composite_entry["name"] = "root"
	create_composite_node(composite_entry)

	tree_dict["child_list"].append(composite_entry)

pp = pprint.PrettyPrinter(indent=4)

def run_gen():
	global default_w_child, max_sub_trees, output_path
	tree_dict = copy.deepcopy(default_w_child)
	tree_dict["type_"] = get_root_type()
	num_sub_trees = random.randint(1, max_sub_trees)
	for i in range(num_sub_trees):
		gen_subtree(tree_dict)
	
	write_expr(output_path, "expr_test.json", tree_dict)


def write_expr(output_path, filename, tree_dict):
	tree_path = output_path + "/" + filename
	Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
	with open(tree_path, 'w') as outfile:
		json.dump(tree_dict, outfile)
	print(f"Tree output to {tree_path}")

def main():
	run_gen()
		
if __name__ == '__main__':
	main()
