import re
from matplotlib import pyplot as plt
import networkx as nx
import copy
import pydot
import os
import csv


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
# TODO: should pull some regex constants from the pipeline constants, hard coded for now
regex_dict = {
    RE_NOTHINGORWHITESPACESTART + INVERTER + RE_ANY: INVERTER,
    RE_NOTHINGORWHITESPACESTART + "Repeat<>" + RE_ANY: REPEAT,
    # must be before Sequence, too lazy to figure out the regex
    RE_NOTHINGORWHITESPACESTART + LATSEQ + RE_ANY: LATSEQ,
    RE_NOTHINGORWHITESPACESTART + SEQUENCE + RE_ANY: SEQUENCE,
    # must be before || and Selector
    RE_NOTHINGORWHITESPACESTART + "\|\| \/ Selector" + RE_ANY: PARSEL,
    RE_NOTHINGORWHITESPACESTART + SELECTOR + RE_ANY: SELECTOR,
    RE_NOTHINGORWHITESPACESTART + "\|\|" + RE_ANY: PARALLEL,
    "(" + RE_NOTHINGORWHITESPACESTART + "A->" + RE_ANY + "|" + RE_NOTHINGORWHITESPACESTART + "action" + RE_ANY + ")": ACTION,
    "*": CONDITION  # catch all, needs to stay in this order as conditions do not have a good identifier
}

def find_min_case(generated_graph, generated_graph_min_case, sim_graph):
    gen_root = get_root_node(generated_graph)
    sim_root = get_root_node(sim_graph)


    gen_subtrees = [get_subtree_graph(
        generated_graph, edges[1]) for edges in generated_graph.out_edges(gen_root)]
    gen_subtrees_min_case = [get_subtree_graph(
        generated_graph_min_case, edges[1]) for edges in generated_graph_min_case.out_edges(gen_root)]
    sim_subtrees = [get_subtree_graph(sim_graph, edges[1])
                    for edges in sim_graph.out_edges(sim_root)]

    Number_condition = remove_all_condition_after_first_in_fallbacks(gen_subtrees_min_case)
    return Number_condition


def get_root_node(graph):
    return [n for n, d in graph.in_degree() if d == 0][0]

def get_subtree_graph(graph, sub_tree_node):
    return copy.deepcopy(nx.bfs_tree(graph, source=sub_tree_node, reverse=False))


def remove_all_condition_after_first_in_fallbacks(gen_subtrees_min_case):
    Number_condition = dict()
    for g, graph in enumerate(gen_subtrees_min_case):
        for node in list(graph.nodes):
            if SELECTOR in node:
                roots = []
                for i, edge in enumerate(graph.out_edges(node)):
                    if i>0:
                        descendants = list(nx.descendants(graph, edge[1]))
                        for descendant in descendants:
                            gen_subtrees_min_case[g].remove_node(descendant)        
                            roots.append(edge[1])
                gen_subtrees_min_case[g].remove_nodes_from(roots)
        properties_sub_tree = get_freq_unique_node_dict(gen_subtrees_min_case[g])
        Number_condition[g] = properties_sub_tree.get('Condition')
    return Number_condition



def get_node_regex_dict():
    return regex_dict


def unique_node_set():
    return get_node_regex_dict().values()


def unique_node_freq_counter():
    return dict.fromkeys(unique_node_set(), 0)

def get_freq_unique_node_dict(graph):
    freq_dict = unique_node_freq_counter()
    node_regex = get_node_regex_dict()
    for i, node in enumerate(graph.nodes):
        if "!" in node:
            node ="action"
        for reg_pat, node_type in node_regex.items():
            if reg_pat == "*" or re.search(reg_pat, node):
                freq_dict[node_type] += 1
                break  # go to next node
    return freq_dict

results_path = "GraphAnalysis/"
if not os.path.exists(results_path):
    os.makedirs(results_path)
    
with open( results_path + "graphAnalysis.csv", "w", encoding='UTF8', newline='') as csvFile:
#with open( results_path + "graphAnalysis.csv", "a", encoding='UTF8', newline='') as csvFile:
    header = ["experiment","RE-BT+F: avg best scenario","RE-BT: avg best scenario" ,"RE-BT+F: avg worst scenario", "RE-BT: avg worst scenario", "MY: #Nodes" , "RE-BT: #Nodes" , "MY: #Conditions" , "RE-BT: #Conditions"  , "MY: #Fallbacks" , "RE-BT: #Fallbacks" , " % of reduced nodes", "RE-BT+F: cf value", "RE:BT: cf value", "% of reduced cf"]
    graph_analysis = csv.writer(csvFile)
    graph_analysis.writerow(header)
    for i in range(0,100):
        if i == 37:
            continue
        seed_path = "sim_data/expr" + str(i) 
        path_to_tree_dot_file_input = seed_path + "/expr" + str(i) + ".dot"
        path_to_tree_dot_file_learned = seed_path + "/output/pipeline_output/5_kFold_5_maxDepth/Pruning/Pruning_0_0/gfactor/behaviortree.dot"
        path_to_tree_dot_file_re_bt = seed_path + "/output/pipeline_output/5_kFold_5_maxDepth/Pruning/Pruning_0_0/behaviortree.dot"

        G_input = nx.nx_pydot.from_pydot(
                pydot.graph_from_dot_file(path_to_tree_dot_file_input)[0])
        G_learned = nx.nx_pydot.from_pydot(
                pydot.graph_from_dot_file(path_to_tree_dot_file_learned)[0])
        G_learned_min_case = nx.nx_pydot.from_pydot(
                pydot.graph_from_dot_file(path_to_tree_dot_file_learned)[0])
        G_re_bt = nx.nx_pydot.from_pydot(
                pydot.graph_from_dot_file(path_to_tree_dot_file_re_bt)[0])
        G_re_bt_min_case = nx.nx_pydot.from_pydot(
                pydot.graph_from_dot_file(path_to_tree_dot_file_re_bt)[0])
        
        print("Starting..")

        print("Experiment number ", i)

        print("Running BT Factor")
        nodes_my_method = len(list(G_learned.nodes))-1
        properties_my_graph = get_freq_unique_node_dict(G_learned)
        Conditions_my_method = find_min_case(G_learned, G_learned_min_case,G_input)
        average_best_scenario_my_method = sum(Conditions_my_method.values())/len(Conditions_my_method)
        tot_conditions_my_method = properties_my_graph.get("Condition")
        average_worst_scenario_my_method =tot_conditions_my_method /len(Conditions_my_method)


        print("\nRunning RE BT")
        nodes_re_bt = len(list(G_re_bt.nodes))-1
        properties_re_bt_graph=get_freq_unique_node_dict(G_re_bt)
        Conditions_re_bt = find_min_case(G_re_bt, G_re_bt_min_case, G_input)
        average_best_scenario_re_bt = sum(Conditions_re_bt.values())/len(Conditions_re_bt)
        tot_conditions_re_bt = properties_re_bt_graph.get("Condition")
        average_worst_scenario_re_bt = tot_conditions_re_bt/len(Conditions_re_bt)


        fallbacks_my_method = properties_my_graph.get("Selector") + properties_my_graph.get("Parallel Selector")
        fallbacks_re_bt = properties_re_bt_graph.get("Selector") + properties_re_bt_graph.get("Parallel Selector")

        cf_my_method =-1
        if fallbacks_my_method!=0 :
            cf_my_method = tot_conditions_my_method/fallbacks_my_method
        cf_re_bt = -1
        if fallbacks_re_bt!=0 :
            cf_re_bt = tot_conditions_re_bt/fallbacks_re_bt
        per_reduced_cf =  (cf_re_bt-cf_my_method)/cf_re_bt*100
       
        per_reduced_nodes =  (nodes_re_bt-nodes_my_method)/nodes_re_bt*100
              
        graph_analysis.writerow([i, average_best_scenario_my_method , average_best_scenario_re_bt, average_worst_scenario_my_method, average_worst_scenario_re_bt, nodes_my_method, nodes_re_bt ,tot_conditions_my_method, tot_conditions_re_bt,  fallbacks_my_method , fallbacks_re_bt,  per_reduced_nodes, cf_my_method, cf_re_bt, per_reduced_cf])

        print("Done with experiment ", i, "\n")

