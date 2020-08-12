from lxml import etree
import numpy as np

def is_leaf_node(dt, node_index):
	return (dt.children_left[node_index] == -1 and dt.children_right[node_index] == -1)

def build_rules_rec(dt, node_index, current_build_path, total_rule_array, feature_names):
	if is_leaf_node(dt, node_index):
		total_rule_array.append([dt.value[node_index], current_build_path])
	else:
		trueRule = feature_names[dt.feature[node_index]] + " <= " + str(dt.threshold[node_index])
		falseRule = feature_names[dt.feature[node_index]] + " > " + str(dt.threshold[node_index])	

		leftPath = current_build_path.copy()
		leftPath.append([trueRule])
		build_rules_rec(dt, dt.children_left[node_index], leftPath, total_rule_array, feature_names)

		rightPath = current_build_path.copy()
		rightPath.append([falseRule])
		build_rules_rec(dt, dt.children_right[node_index], rightPath, total_rule_array, feature_names)

def dt_to_rules(dt, feature_names):
	total_rule_array = []
	build_rules_rec(dt, 0, [], total_rule_array, feature_names)
	return total_rule_array

def add_child(parent, child):
	parent.append(child)

def create_behavior_tree():
	frame = etree.Element("root")
	tree = etree.ElementTree(frame)
	frame.set('main_tree_to_execute', 'MainTree')

	main_behavior = etree.Element("BehaviorTree")
	main_behavior.set('ID', 'MainTree')
	frame.append(main_behavior)

	return main_behavior, tree

def parallel_node(name, parent):
	parallel_node = etree.Element("Parallel")
	parallel_node.set('name', name)
	add_child(parent, parallel_node)
	return parallel_node

def sequence_node(name, parent):
	sequence_node = etree.Element("Sequence")
	sequence_node.set('name', name)
	add_child(parent, sequence_node)
	return sequence_node

def condition_node(name, parent):
	condition_node = etree.Element("Condition")
	condition_node.set('ID', name)
	condition_node.set('name', name)
	condition_node.set('message', "")
	add_child(parent, condition_node)
	return condition_node

def action_node(name, parent):
	action_node = etree.Element("Action")
	action_node.set('ID', name)
	action_node.set('name', name)
	action_node.set('message', "")
	add_child(parent, action_node)
	return action_node

def fallback_node(name, parent):
	fallback_node = etree.Element("Fallback")
	fallback_node.set('name', name)
	add_child(parent, fallback_node)
	return fallback_node

def find_max_index(numpy_1D_array):
	max_element = np.amax(numpy_1D_array)
	index = np.where(numpy_1D_array == max_element)
	return index[0][0]

def bt_espresso_mod(dt, feature_names, label_names):
	rules = dt_to_rules(dt, feature_names)
	main_behavior, tree = create_behavior_tree()
	root = fallback_node('root', main_behavior)

	for rule in rules:
		action = rule[0][0] # will return something like [0. 0. 128. 0. 3. 0.]
		label_index = find_max_index(action) # would return 2
		label = label_names[label_index]
		newRule = sequence_node(str(label), root)
		conditions = sequence_node("Conditions", newRule)
		for decision in rule[1]:
			conditionPart = condition_node(decision[0], conditions)
		add_action = action_node(str(label), newRule)

	return tree

def save_tree(tree, filename):
	with open (filename, "wb") as file: tree.write(file, pretty_print = True)

