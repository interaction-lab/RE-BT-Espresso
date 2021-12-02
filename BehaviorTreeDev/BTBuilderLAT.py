from BehaviorTreeDev.BTBuilderHelpers import get_cycles_node_name
import networkx as nx
import pipeline_constants as constants
from BTBuilderGlobals import cyclenode_to_path_dict, expr_name

def find_all_paths(outgoing_edge_dict):
    if len(outgoing_edge_dict) == 0:
        return [], []

    global cycle_node_to_path_dict # [cycle_node] -> cycle path list
    source_nodes = []
    end_nodes = []
 
    graph = create_di_graph(outgoing_edge_dict)
    dag_graph_from_cycles(graph, cyclenode_to_path_dict)
    find_source_and_end_nodes(source_nodes, end_nodes, graph)
    non_cycles = find_non_cycle_paths(source_nodes, end_nodes, graph)
    return non_cycles, cyclenode_to_path_dict

def find_non_cycle_paths(source_nodes, end_nodes, graph):
    non_cycles = list()
    for source in source_nodes:
        for end in end_nodes:
            if end == source:
                non_cycles.append([source]) # singular node, not caught in all_simple_paths
                continue
            for path in nx.all_simple_paths(graph, source, end):
                non_cycles.append(path)
    return non_cycles

def find_source_and_end_nodes(source_nodes, end_nodes, graph):
    for node in graph.nodes:

        if graph.in_degree(node) == 0:
            source_nodes.append(node)
        if graph.out_degree(node) == 0: # cannot be elif, can be singular node in graph with node
            end_nodes.append(node)

def create_di_graph(outgoing_edge_dict):
    graph = nx.DiGraph()
    for d_node in outgoing_edge_dict:
        for s_node in outgoing_edge_dict[d_node]:
            graph.add_edge(s_node, d_node)
    return graph

def is_cycle_node(node):
    return constants.CYLCE_NODE in node


import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def dag_graph_from_cycles(graph, cyclenode_to_path_dict):
    cycles = list(nx.simple_cycles(graph))
    while len(cycles) > 0:
        for cycle in cycles:
            n_name = get_cycles_node_name()
            graph.add_node(n_name)
            remove_cycle(graph, cycle, n_name)
            cyclenode_to_path_dict[n_name] = cycle
        cycles = list(nx.simple_cycles(graph))
        if len(cycles > 0):
            global expr_name
            print("raise multi_cylced~||~------------------------------------------------------------------------")
            print(expr_name)
            eprint("raise multi_cylced~||~------------------------------------------------------------------------")
            eprint(expr_name)
            raise "multi_cylced"


def remove_cycle(graph, cycle, n_name):
    nodes_in_cycle_set = set(cycle) # avoid self looping
    for node in cycle:
        for edge in graph.in_edges(node):
            if edge[0] not in nodes_in_cycle_set:
                graph.add_edge(edge[0], n_name)
        for edge in graph.out_edges(node):
            if edge[1] not in nodes_in_cycle_set:
                graph.add_edge(n_name, edge[1])
    graph.remove_nodes_from(cycle)
