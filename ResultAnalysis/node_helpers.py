import re
import networkx as nx
import time
import threading

SEQUENCE = "Sequence"
SELECTOR = "Selector"
PARALLEL = "Parallel"
ACTION = "Action"
INVERTER = "Inverter"
CONDITION = "Condition"
PARSEL = "Parallel Selector"
REPEAT = "Repeater"
LATSEQ = "LAT Sequence"

RE_NOTHINGORWHITESPACESTART = "(?<!\S)"
RE_NOTHINGORWHITESPACEEND = "(?!\S)"
RE_ANY = "*"

# [regular expression] -> node_type_str
#TODO: should pull some regex constants from the pipeline constants, hard coded for now
regex_dict = {
        RE_NOTHINGORWHITESPACESTART + INVERTER + RE_ANY : INVERTER,
        RE_NOTHINGORWHITESPACESTART + "Repeat<>" + RE_ANY : REPEAT,
        RE_NOTHINGORWHITESPACESTART + LATSEQ + RE_ANY : LATSEQ, # must be before Sequence, too lazy to figure out the regex
        RE_NOTHINGORWHITESPACESTART + SEQUENCE + RE_ANY : SEQUENCE,
		RE_NOTHINGORWHITESPACESTART + "\|\| \/ Selector" + RE_ANY : PARSEL, # must be before || and Selector
        RE_NOTHINGORWHITESPACESTART + SELECTOR + RE_ANY : SELECTOR,
        RE_NOTHINGORWHITESPACESTART + "\|\|" + RE_ANY : PARALLEL,
        "(" + RE_NOTHINGORWHITESPACESTART + "A->" + RE_ANY + "|" + RE_NOTHINGORWHITESPACESTART + "action" + RE_ANY + ")" : ACTION,
        "*": CONDITION # catch all, needs to stay in this order as conditions do not have a good identifier
}

def get_node_regex_dict():
    return regex_dict


def unique_node_set():
    return get_node_regex_dict().values()

def unique_node_freq_counter():
    return dict.fromkeys(unique_node_set(), 0)


def get_freq_unique_node_dict(graph):
	freq_dict = unique_node_freq_counter()
	node_regex = get_node_regex_dict()
	for node in graph.nodes:
		for reg_pat, node_type in node_regex.items():
			if reg_pat == "*" or re.search(reg_pat, node):
				freq_dict[node_type] += 1
				break # go to next node
	return freq_dict

def num_unique_nodes(graph):
	return sum(x > 0 for x in get_freq_unique_node_dict(graph).values())

def total_num_nodes(graph):
    return len(graph.nodes)

def get_root_node(graph):
    return [n for n, d in graph.in_degree() if d == 0][0]

def get_num_subtrees_from_root(graph):
    return len(graph.edges(get_root_node(graph)))


def get_subtree_graph(graph, sub_tree_node):
    return nx.bfs_tree(graph, source=sub_tree_node, reverse=False)

def find_graph_sim(generated_graph, sim_graph):
    # define node match function
    # define edge match function
    gen_root = get_root_node(generated_graph)
    sim_root = get_root_node(sim_graph)

    gen_subtrees = [get_subtree_graph(generated_graph, edges[1]) for edges in generated_graph.out_edges(gen_root)]
    sim_subtrees = [get_subtree_graph(sim_graph, edges[1]) for edges in sim_graph.out_edges(sim_root)]

    # possibly split all expriment sub_trees as well

    max_iters = 3 # tunable, possibly look at timeouts

    for tree in gen_subtrees:
        name_dict = dict(zip(tree.nodes, tree.nodes))
        nx.set_node_attributes(tree,name_dict,'label')
        
    min_score = gen_min_edit_distance_for_all_subtrees(sim_graph, gen_subtrees, max_iters)
    return min_score

# make it so that we rename everything from each first
# DONE: expr conditionals should have same name as env etc
# DONE: LAT Sequence, sequence, selector, ||, conditional, action
# TODO: remove all inverters
# TODO: repeaters -> I think I should just do the following:
#                   1) add Repeat<> in each of the expr
#                   2) special case that in the sim for behavior to repeat a few times
# TODO: sel par replaceable -> possibly move this to say || in it and Selector specifically? or special case in sim
#                              I think special casing this in the BT sim and having both actions go below... idk

# match everything but invert conditionsal, should just remove from graph
# sequence
# selector
# par selector

# removes all everyhting except[alphanumeric, '|']
pattern = re.compile('[^A-Za-z0-9\|]+')
def custom_node_match(gen_node, sim_node):
    return pattern.sub("", sim_node['label']) in gen_node['label']

def gen_min_edit_distance_for_all_subtrees(sim_graph, gen_subtrees, max_iters):
    min_score = None
    for g_tree in gen_subtrees:
        i = 0
        for score in nx.optimize_graph_edit_distance(g_tree, sim_graph, node_match=custom_node_match):
            if min_score == None or score < min_score:
                min_score = score
            i += 1
            if i == max_iters:
                break
    return min_score


