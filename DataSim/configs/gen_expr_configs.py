import random
import json
import os
from pathlib import Path
import pprint
import copy

max_sub_trees = 3
max_things_in_composite = 5
max_par_actions = 3

num_actions = 5
action_set = ["action_" + str(i) for i in range(num_actions)]
num_conditions = 5
condition_set = ["/env_state_var_" + str(i+1) for i in range(num_conditions)]

root_set = ["parallel", "sequence"]
# sekector omitted, only used for conditions
composite_set = ["sequence", "repeater"]
leaf_set = ["condition", "action"]

default_entry = {
	"name": "DEFAULT",
	"type_": "DEFAULT",
}

default_w_child = copy.deepcopy(default_entry)
default_w_child["child_list"] = []

default_w_cond = copy.deepcopy(default_entry)
default_w_cond["p_success"] = 1
default_w_cond["inverted"] = False
default_w_cond["threshold"] = 0.5

output_path = "./experiments"

total_num_experiments = 100
expr_num = range(5, total_num_experiments)


def reset_sets():
	global action_set, condition_set
	action_set = ["action_" + str(i) for i in range(num_actions)]
	condition_set = ["/env_state_var_" +
					 str(i+1) for i in range(num_conditions)]


def get_root_type():
	global root_set
	return random.sample(root_set, 1)[0]


def choose_composite_type():
	global composite_set
	return random.sample(composite_set, 1)[0]


def choose_random_action():
	global action_set
	rand_action = random.sample(action_set, 1)[0]
	action_set.remove(rand_action)
	return rand_action


def choose_random_condition():
	global condition_set
	rand_cond = random.sample(condition_set, 1)[0]
	condition_set.remove(rand_cond)
	return rand_cond


def create_parsel(leaf_entry):
	global max_par_actions
	leaf_entry["type_"] = "parsel"
	leaf_entry["name"] = leaf_entry["type_"]
	child_list = []
	for i in range(0, random.randint(2, max_par_actions)):
		my_entry = copy.deepcopy(default_w_cond)
		create_action(my_entry, False)
		if my_entry != None:
			child_list.append(my_entry)
	leaf_entry["child_list"] = copy.deepcopy(child_list)


def create_action(leaf_entry, include_parsel=True):
	if len(action_set) == 0:
		leaf_entry = None
	elif random.random() < 0.3 and len(action_set) >= 2 and include_parsel:
		create_parsel(leaf_entry)
	else:
		leaf_entry["type_"] = "action"
		leaf_entry["name"] = choose_random_action()


def create_single_condition(leaf_entry):
	leaf_entry["type_"] = "condition"
	leaf_entry["name"] = choose_random_condition()
	leaf_entry["target_state"] = leaf_entry["name"]
	leaf_entry["inverted"] = random.random() > 0.3


def create_condition(leaf_entry):
	if random.random() < 0.3 and len(condition_set) >= 2:  # configurable for % of selector conditions
		leaf_entry["type_"] = "selector"
		leaf_entry["name"] = leaf_entry["type_"]

		leaf_one = copy.deepcopy(default_w_cond)
		leaf_two = copy.deepcopy(default_w_cond)
		create_single_condition(leaf_one)
		create_single_condition(leaf_two)
		leaf_entry["child_list"] = [leaf_one, leaf_two]
	else:
		create_single_condition(leaf_entry)


def create_leaf(leaf_entry):
	if random.random() < 0.4 or len(condition_set) == 0:
		create_action(leaf_entry)
	else:
		create_condition(leaf_entry)


def create_composite_node(composite_entry):
	global default_entry, max_things_in_composite
	child_list = []

	rand_num_things = random.randint(2, max_things_in_composite)
	for i in range(0, rand_num_things):
		my_entry = copy.deepcopy(default_w_cond)
		if i == rand_num_things - 1:
			create_action(my_entry)  # last thing always action
		else:
			create_leaf(my_entry)

		if my_entry != None:
			child_list.append(my_entry)

	composite_entry["child_list"] = copy.deepcopy(child_list)


def gen_subtree(tree_dict):
	# compositechoice
	composite_entry = copy.deepcopy(default_w_child)
	composite_entry["type_"] = choose_composite_type()
	composite_entry["name"] = composite_entry["type_"]
	create_composite_node(composite_entry)
	tree_dict["child_list"].append(composite_entry)


pp = pprint.PrettyPrinter(indent=4)


def already_genned_tree(tree_dict):
	global all_tree_dicts
	for d in all_tree_dicts:
		if d == tree_dict:
			return True
	return False


def run_gen(expr_ext_name):
	global default_w_child, max_sub_trees, output_path, all_tree_dicts
	tree_dict = copy.deepcopy(default_w_child)
	tree_dict["type_"] = get_root_type()
	tree_dict["name"] = tree_dict["type_"] + "_root"
	num_sub_trees = random.randint(2, max_sub_trees)
	for i in range(0, num_sub_trees):
		gen_subtree(tree_dict)
		reset_sets()

	if already_genned_tree(tree_dict):  # make sure no duplicates
		tree_dict = dict()
		print("Duplicate tree generated, regenerating")
		run_gen(expr_ext_name)
		return  # none inf recur

	all_tree_dicts.append(copy.deepcopy(tree_dict))
	write_expr(output_path, "expr" + expr_ext_name + ".json", tree_dict)


all_tree_dicts = []


def run_gen_all():
	for i in expr_num:
		run_gen(str(i))


def write_expr(output_path, filename, tree_dict):
	tree_path = output_path + "/" + filename
	Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
	with open(tree_path, 'w') as outfile:
		json.dump(tree_dict, outfile)
	print(f"Tree output to {tree_path}")


def main():
	run_gen_all()


if __name__ == '__main__':
	main()
