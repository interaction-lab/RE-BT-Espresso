from lxml import etree
import numpy as np
import copy
from numpy.core.arrayprint import _void_scalar_repr
from queue import Queue
import networkx as nx

import py_trees.decorators
import py_trees.display

import re
import pyeda
from pyeda.inter import *
from pyeda.boolalg.expr import _LITS


import pipeline_constants as constants

# something to do with grabbing an inverted variable in process leaf or process non leaf leading to things that should not be ther, maybe a counter issue?


binary_feature_set = set()

def find_max_index(numpy_1D_array):
    """Finds and returns first max argument index in numpy array

    Args:
        numpy_1D_array (np.arr[int]): numpy array to find max of
        ex: [[  0.   100.  194.   194.   0.   0.]] -> 2

    Returns:
    int	: index of max element in array
    """
    max_element = np.amax(numpy_1D_array)
    index = np.where(numpy_1D_array == max_element)
    return index[1][0]

def find_max_indices_given_percent(numpy_1D_array):
    """Finds array of max indices within a given percent
       ex. [[10, 0, 9.5, 7]], 0.1 -> [0,2]

    Args:
        numpy_1D_array (np.arr[int]): numpy array to find max of
        action_diff_tolerance (float): percent [0.0-1.0] to take values of

    Returns:
        np.arr(int) : indices of array falling within percdiff 
    """
    assert constants.ACTION_DIFF_TOLERANCE >= 0 and constants.ACTION_DIFF_TOLERANCE <= 1.0
    tmp_arr = numpy_1D_array[0]
    min_val = np.amax(numpy_1D_array) * (1.0 - constants.ACTION_DIFF_TOLERANCE)
    indices = np.where(tmp_arr >= min_val)[0]
    return indices

def add_condition_to_action_dictionary(dictionary, key, value):
    """Adds condition to [action] -> condition string dictionary

    Args:
        dictionary (dict[str,str]): action dictionary from action -> condition string
        key (str): action string
        value (str): condition string
    """
    if not key in dictionary:
        dictionary[key] = value
    elif value != "": # deal with empty conditions
        dictionary[key] = dictionary[key] + " | " +  value

def invert_expression(exp):
    """Inverts and returns logical operator expressions
       ex. "<" -> ">="

    Args:
        exp (str): original conditional expression

    Returns:
        str: inverted string representation of original conditional expression
    """
    if ">=" in exp:
        return exp.replace(">=", "<")
    elif "<=" in exp:
        return exp.replace("<=", ">")
    elif ">" in exp:
        return exp.replace(">", "<=")
    elif "<" in exp:
        return exp.replace("<", ">=")
    elif "True" in exp:
        return exp.replace("True", "False")
    elif "False" in exp:
        return exp.replace("False", "True")
    else:
        return exp

def is_leaf_node(dt, node_index):
    """Checks if node at node_index is a leaf node to a DecisionTree

    Args:
        dt (sklearn.DecisionTree): decision tree to be examined
        node_index (int): index of node in dt

    Returns:
        bool : whether node at index is a leaf node in dt
    """
    return (dt.children_left[node_index] == -1
            and dt.children_right[node_index] == -1)
56  
def get_key(dictionary, val):
    for key, value in dictionary.items():
        if val == value:
            return key
    return "key doesn't exist"

def is_last_action_taken_condition(condition):
    return constants.LAST_ACTION_TAKEN_COLUMN_NAME in condition and not "No Entry" in condition

# [variable_symbol] -> condition
lat_cond_lookup = dict()
def build_last_action_taken_dict(condition, cond_symbol):
    global lat_cond_lookup
    if is_last_action_taken_condition(condition) and cond_symbol not in lat_cond_lookup:
        lat_cond_lookup[cond_symbol] = condition.replace(constants.LAST_ACTION_TAKEN_COLUMN_NAME + "_", "")

def dt_to_pstring_recursive(dt, node_index, current_pstring, sym_lookup, action_to_pstring, feature_names, label_names):
    if is_leaf_node(dt, node_index):
        process_leaf_node(dt, node_index, label_names, action_to_pstring, current_pstring)
    else:
        process_non_leaf_node(dt, node_index, feature_names, sym_lookup, current_pstring, action_to_pstring, label_names)

def process_non_leaf_node(dt, node_index, feature_names, sym_lookup, current_pstring, action_to_pstring, label_names):
    global lat_cond_lookup
    true_rule = None
    if is_bool_feature(dt, node_index, feature_names):
        # the == False exists because the tree denotes it as "IsNewExercise_True <= 0.5" which, when true, is actually Is_NewExercise_False
        true_rule = invert_expression(feature_names[dt.feature[node_index]])
    else:
        true_rule = feature_names[dt.feature[node_index]] + " <= " + str(
            round(dt.threshold[node_index], 3))
    false_rule = invert_expression(true_rule)

    true_letter = None
    false_letter = None

    # Note: this is very jank, we invert the rules of the dt for true letters to be ~ because of set up of dtree
    if (not true_rule in sym_lookup) and (not false_rule in sym_lookup):
        add_condition_to_action_dictionary(
            sym_lookup, 
            false_rule,
            get_current_var_name())

    # bug with adding vars multiple times maybe here, likely needs to be moved up, maybe not
    if false_rule in sym_lookup:
        false_letter = sym_lookup.get(false_rule)
        true_letter = "~" + false_letter
    
    build_last_action_taken_dict(false_rule, false_letter) # uses jank from above

    left_pstring = true_letter if current_pstring == "" else current_pstring + \
        " & " + true_letter
    right_pstring = false_letter if current_pstring == "" else current_pstring + \
        " & " + false_letter
    
    # traverse left side of tree (true condition)
    dt_to_pstring_recursive(dt,
                            dt.children_left[node_index],
                            left_pstring,
                            sym_lookup,
                            action_to_pstring,
                            feature_names,
                            label_names)

    # traverse right side of tree (false condition)
    dt_to_pstring_recursive(dt,
                            dt.children_right[node_index],
                            right_pstring,
                            sym_lookup,
                            action_to_pstring,
                            feature_names,
                            label_names)
    # remove all LAT from string


var_cycle_count = 0
def get_current_var_name():
    global var_cycle_count    
    tmp = "VAR" + str(var_cycle_count)
    var_cycle_count += 1
    return tmp


def add_to_vec_hash_dict(dictionary, key, value):
    '''Adds to a dictionary of the following, appending to end of set
    key: -3
    value: -1
    dictionary: {
        -3 : {4,6}
    }
    result: {
        -3 : {4,6,-1}
    }
    '''
    if key not in dictionary:
        dictionary[key] = {value}
    else:
        dictionary[key].add(value)


def process_leaf_node(dt, node_index, label_names, action_to_pstring, current_pstring):
    max_indices = find_max_indices_given_percent(dt.value[node_index])
    action = ""
    for i in max_indices:
        if action != "":
            action += constants.MULTI_ACTION_PAR_SEL_SEPERATOR
        # else: -> I think this is an old bug, may or may not be fixed, likely from physical data issue
        #     print(action)
        action += str(label_names[i])
    # process last action taken here?
    add_condition_to_action_dictionary(
        action_to_pstring, 
        action, 
        current_pstring)

def is_last_action_taken_no_entry(condition):
    return condition == constants.LAST_ACTION_TAKEN_COLUMN_NAME_NO_ENTRY

def is_bool_feature(dt, node_index, feature_names):
    global binary_feature_set
    name = feature_names[dt.feature[node_index]]
    return name in binary_feature_set or is_last_action_taken_condition(name) or ("True" in name)

# sym_lookup format:
# {'tsla <= 19.14': 'a',
#  'exerciseSubmissionResult_Correct == False': 'b',
#  'exerciseSubmissionResult_No Entry == False': 'c',
#  'ScaffLeft <= 0.5': 'd', ...}

# action_to_pstring:
# {'Dialogue: 3': 'a & b & c & d & e',
#  'PPA': 'a & b & c & d & ~e | ~a & h & i & ~j | ~a & ~h',
#  'Dialogue: 4': 'a & b & c & ~d | a & b & ~c & f & ~g',
#  'Dialogue: 1': 'a & b & ~c & f & g | a & b & ~c & ~f', ...}

def dt_to_pstring(dt, feature_names, label_names):
    sym_lookup = {}
    action_to_pstring = {}
    dt_to_pstring_recursive(dt, 0, "", sym_lookup,
                            action_to_pstring, feature_names, label_names)
    return sym_lookup, action_to_pstring

def get_common_conditions(condition_pstring):
    if condition_pstring.to_ast()[0] == constants.OR:
        all_condition_sets = []
        for operand in condition_pstring.to_ast()[1:]:
            list_conditions = None
            if operand[0] == constants.AND:
                list_conditions = [condition[1] for condition in operand[1:]]
            else:
                list_conditions = [operand[1]]
            all_condition_sets.append(list_conditions)
        return list(set.intersection(*map(set, all_condition_sets))), all_condition_sets
    else:
        return [], []

def int_to_condition(int_condition):
    return str(_LITS[int_condition])

def is_float_key(k_in):
    return "<=" in k_in

def get_key_from_float_expr(k_in):
    return k_in.split("<=")[0], float(k_in.split("<=")[1][1:])

def generate_all_containing_float_variable_dict(sym_lookup):
    containing_float_dict = {}
    feature_look_up = {}
    for key, value in sym_lookup.items():
        if is_float_key(key):
            f_key, f_val = get_key_from_float_expr(key)
            if f_key not in feature_look_up:
                feature_look_up[f_key] = [(f_val, value)]
            else:
                feature_look_up[f_key].append((f_val, value))

    for f in feature_look_up:
        feature_look_up[f].sort(key=lambda x: x[0])
        l = feature_look_up[f]
        for i in range(len(l) - 1):
            tup = l[i]
            sym = tup[1]
            containing_float_dict[sym] = {x[1] for x in l[i+1:]}
        feature_look_up[f].sort(key=lambda x: x[0], reverse=True)
        for i in range(len(l) - 1):
            tup = l[i]
            sym = tup[1]
            containing_float_dict['~' + sym] = {'~' + x[1] for x in l[i+1:]}
    return containing_float_dict

def remove_float_contained_variables(sym_lookup, pstring_dict):
    """Removes float variables that "consume" the others
       ex.: a = (f1 < 5); b = (f1 < 2); condition = (a & b)
       -> condition = (b) due to b "consuming" a

    Args:
        sym_lookup (dict[str,str]): dictionary from symbol to condition string (e.g., {"a" : "f1 < 5"})
        pstring_dict (dict[str,str]): dictionary from action symbol to set of conditions (e.g., {"ACTION1" : "(a & b) | c"})

    Returns:
        dict[str,str]: reduced/consumed dictionary of actions to condition strings
    """
    # get dictionary of all replaceable factors
    containing_float_dict = generate_all_containing_float_variable_dict(
        sym_lookup)

    # find all conditions with both variables
    # remove lower variable
    for action, condition_pstring in pstring_dict.items():
        if(condition_pstring == ""):
            continue # deal with empty conditions likely from LAT, still valid
        new_pstring = "("
        new_pstring_list = []

        # processes And well
        expr_to_process = None
        if condition_pstring.to_ast()[0] == constants.OR:
            expr_to_process = condition_pstring.to_ast()[1:]
        else:
            expr_to_process = [condition_pstring.to_ast()]

        for dnf in expr_to_process:
            to_remove_set = set()

            if dnf[0] != constants.AND:  # condition is only literal
                new_pstring_list.append([int_to_condition(dnf[1])])
                continue

            # Build remove set
            for lit_tuple in dnf[1:]:
                letter_key = int_to_condition(lit_tuple[1])
                if letter_key in containing_float_dict:
                    to_remove_set.update(containing_float_dict[letter_key])

            # Remove all contained floats
            new_pstring_list.append([int_to_condition(
                lit_tup[1]) for lit_tup in dnf[1:] if int_to_condition(lit_tup[1]) not in to_remove_set])

        ors = str(new_pstring_list).replace(',', ' &')\
            .replace("[", "(")\
            .replace("]", ")")\
            .replace(") & (", ") | (")\
            .replace("\'", "")
        new_pstring += ors + ")"
        pstring_dict[action] = expr(new_pstring).to_nnf()
    return pstring_dict

def factorize_pstring(pstring_dict):
    for action, condition_pstring in pstring_dict.items():
        if(condition_pstring == ""):
            continue # deal with empty conditions likely from LAT, still valid
        can_simplify = condition_pstring.to_ast()[0] == constants.OR
        conditions_in_all, all_condition_sets = get_common_conditions(
            condition_pstring)
        if can_simplify and conditions_in_all:
            new_pstring = "("
            for common_condition in conditions_in_all:
                new_pstring += str(_LITS[common_condition]) + " & "
                [condition_set.remove(common_condition)
                 for condition_set in all_condition_sets]

            # [[3, -4], [-3, 9, -10]] -> [['c', '~d'], ['~c', 'f', '~g']]
            all_condition_sets_char = [list(
                map(int_to_condition, condition_set)) for condition_set in all_condition_sets]

            # [['c', '~d'], ['~c', 'f', '~g']] -> ((c & ~d) | (~c & f & ~g))
            ors = str(all_condition_sets_char).replace(',', ' &')\
                                              .replace("[", "(")\
                                              .replace("]", ")")\
                                              .replace(") & (", ") | (")\
                                              .replace("\'", "")

            new_pstring += ors + ")"
            pstring_dict[action] = expr(new_pstring).to_nnf()

    return pstring_dict

# Used to give unique names to selector/sequence/inverter nodes to avoid stars
node_name_counter = 0
def get_node_name_counter():
    global node_name_counter
    _ = f"({node_name_counter})"
    node_name_counter += 1
    return _

def make_condition_node(sym_lookup_dict, every_operand):
    need_inverter = False
    value = str(ast2expr(every_operand))
    if value[0] == "~":
        need_inverter = True
        value = value[1:]

    condition = get_key(sym_lookup_dict, value)

    node = py_trees.behaviours.Success(name=condition)
    if need_inverter:
        node = py_trees.decorators.Inverter(
            node, name="Inverter" + get_node_name_counter())

    return node

def recursive_build(pstring_expr, sym_lookup_dict):
    operator = pstring_expr.to_ast()[0]
    new_branch = None
    recursive = False
    if operator == constants.AND:
        recursive = True
        new_branch = py_trees.composites.Sequence(
            name="Sequence" + get_node_name_counter())
    elif operator == constants.OR:
        recursive = True
        new_branch = py_trees.composites.Selector(
            name="Selector" + get_node_name_counter())
    else:
        new_branch = make_condition_node(
            sym_lookup_dict, pstring_expr.to_ast())

    if recursive:
        for every_operand in pstring_expr.to_ast()[1:]:
            if every_operand[0] == constants.AND or every_operand[0] == constants.OR:
                node = recursive_build(
                    ast2expr(every_operand), sym_lookup_dict)
                new_branch.add_child(node)
            else:
                condition_node = make_condition_node(
                    sym_lookup_dict, every_operand)
                new_branch.add_child(condition_node)

    return new_branch

def cleaned_action_behavior(action):
    return py_trees.behaviours.Success(
        name=constants.ACTION_NODE_STR + re.sub('[^A-Za-z0-9]+', '', action))

def generate_action_nodes(action):
    last_action_taken_node = None
    # TODO: I think this is done/deprecated
    if constants.LAST_ACTION_TAKEN_SEPERATOR in action:
        split_list = action.split(constants.LAST_ACTION_TAKEN_SEPERATOR)
        last_action_taken = split_list[0]
        action = split_list[1]
        last_action_taken_node = cleaned_action_behavior(last_action_taken)

    action_list = action.split(constants.MULTI_ACTION_PAR_SEL_SEPERATOR)
    seq_for_mult_action_node = None
    if len(action_list) > 1:
        seq_for_mult_action_node = py_trees.composites.Selector(
        name=constants.SEL_PAR_REPLACEABLE_NAME + get_node_name_counter())
        for a in action_list:
            seq_for_mult_action_node.add_child(cleaned_action_behavior(a))
    else:
        seq_for_mult_action_node = cleaned_action_behavior(action)
    
    final_node = seq_for_mult_action_node
    if last_action_taken_node != None:
        seq = py_trees.composites.Sequence(name=constants.LAT_SEQ_NAME + get_node_name_counter())
        seq.add_child(last_action_taken_node)
        seq.add_child(seq_for_mult_action_node)
        final_node = seq
    return final_node

def pstring_to_btree(action_dict, sym_lookup_dict):
    root = py_trees.composites.Parallel(name="|| Root")
    
    for action in action_dict:
        root.add_child(create_action_seq_node(action, action_dict, sym_lookup_dict))
    return root

def create_action_seq_node(action, action_dict, sym_lookup_dict):
        if(action not in action_dict or action_dict[action] == ""):
            return generate_action_nodes(action) # empty condition set likely from LAT, still valid, deal and continue
        
        top_conditional_seq_node = recursive_build(
            action_dict[action], sym_lookup_dict)

        final_behavior_node = None

        if not isinstance(top_conditional_seq_node, py_trees.composites.Sequence):
            top_seq_node_addition = py_trees.composites.Sequence(
                name="Sequence")
            top_seq_node_addition.add_child(top_conditional_seq_node)
            final_behavior_node = top_seq_node_addition
        else:
            final_behavior_node = top_conditional_seq_node

        final_behavior_node.add_child(generate_action_nodes(action))
    
        return final_behavior_node

def max_prune(dt):
    return is_leaf_node(dt, 0)

def convert_expr_ast_to_str_rep(expr_ast):
    # Note this only works for dnf expressions, maybe we will fix this bleh
    result = ""
    if expr_ast == "" or expr_ast == None:
        print("This should not happen, should pass in ast with at least one literal, returning empty string, likely will break rest of algo")
        return result
    elif(expr_ast[0] == constants.AND):
        list_conditions = [int_to_condition(condition[1]) for condition in expr_ast[1:]]
        result = " & ".join(list_conditions)
    elif(expr_ast[0] == constants.OR):
        # loop through all literals and join
        res_str_list = []
        for and_expr in expr_ast[1:]:
            res_str_list.append(convert_expr_ast_to_str_rep(and_expr))
        result = " | ".join(res_str_list)
    else: # single literal
        result = str(int_to_condition(expr_ast[1]))
    return result

def convert_actions_back_to_expr_rep(action_minimized):
    for action in action_minimized:
        if isinstance(action_minimized[action], str):
            action_minimized[action] = expr(action_minimized[action])

act_to_lat_sets_dict = dict() # 

def contains_latcond(str_rep_cond):
    for key in lat_cond_lookup:
        # (?<!~) is "is not preceded with ~" to avoid inverted conditions 
        # (?!\S) is nothing or whitespace to avoid VAR1 - VAR10 issue
        key_matches = re.findall("(?<!~)" + key + "(?!\S)", str_rep_cond)
        if len(key_matches) > 0:
            return key_matches[0]
    return ""

def add_cond_to_double_dict(dictionary, key1, key2, val):
    # check if val would lead to issue #91 aka it is a 1 in expr, 
    # this would turn all vals in | condition to 1
    if type(expr(val)) ==  pyeda.boolalg.expr._One:
        return
    if key1 in dictionary:
        if key2 in dictionary[key1]:
            dictionary[key1][key2] += " | " + val
        else:
            dictionary[key1][key2] = val
    else:
        dictionary[key1] = dict()
        dictionary[key1][key2] = val

def convert_double_dict_to_expr(dictionary):
    for key1 in dictionary:
        for key2 in dictionary[key1]:
            dictionary[key1][key2] = expr(dictionary[key1][key2])

act_lat_conditions_dict = dict() # [action][lat_action] -> conditions that came with lat minus lat cond
def create_action_min_wo_lat_dict(action_minimized):
    global act_lat_conditions_dict
    global lat_cond_lookup
    global act_to_lat_sets_dict # [lat_action] -> prior action

    action_min_wo_lat_dict = dict()
    for action, condition in action_minimized.items():
        cond_list = convert_expr_ast_to_str_rep(condition.to_ast()).split('|')
        for cond in cond_list:
            latcond = contains_latcond(cond)
            if latcond != "":
                final_cond = remove_all_lat_conditions(cond)
                add_cond_to_double_dict(action_min_wo_lat_dict, action, lat_cond_lookup[latcond], final_cond)
                add_to_vec_hash_dict(act_to_lat_sets_dict, action, lat_cond_lookup[latcond])
    
    convert_double_dict_to_expr(action_min_wo_lat_dict)
    return action_min_wo_lat_dict

def remove_all_lat_conditions(final_cond):
    for key in lat_cond_lookup:
        final_cond = re.sub("(?<!~)" + key + "(?!\S)", " 1 " , final_cond)
        final_cond = re.sub("~" + key + "(?!\S)", " 1 ", final_cond)
    return final_cond

def minimize_bool_expression(sym_lookup, action_to_pstring):
    action_minimized = {}
    espresso_reduction(action_to_pstring, action_minimized)
    action_minimized = remove_float_contained_variables(
        sym_lookup, action_minimized)
    action_min_wo_lat_dict = create_action_min_wo_lat_dict(action_minimized)
    action_minimized = factorize_pstring(
        action_minimized)
    dict_copy = dict(action_min_wo_lat_dict)
    for action in dict_copy:
        action_min_wo_lat_dict[action]= factorize_pstring(action_min_wo_lat_dict[action])
    return action_minimized, action_min_wo_lat_dict

def espresso_reduction(action_to_pstring, action_minimized):
    for action in action_to_pstring:
        if action_to_pstring[action] == "":
            action_minimized[action] = ""
            continue # no conditions, likely a LAT, continue
        expression = expr(action_to_pstring[action])
        # happens in case of VARX | ~VARX
        if(not expression.is_dnf() or type(expression) == pyeda.boolalg.expr._Zero):
            continue
        dnf = expression.to_dnf()
        action_minimized[action] = espresso_exprs(dnf)[0]

def update_freq_dict(dictionary, key, val):
    if key in dictionary:
        dictionary[key] += val
    else:
        dictionary[key] = val

cycle_node_counter = 0
def get_cycles_node_name():
    global cycle_node_counter
    name = constants.CYLCE_NODE + str(cycle_node_counter)
    cycle_node_counter += 1
    return name

def find_all_paths(outgoing_edge_dict):
    if len(outgoing_edge_dict) == 0:
        return [], [], []

    source_nodes = []
    end_nodes = []
    cyclenode_to_path_dict = dict() # [cycle_node] -> cycle path list
 
    graph = create_di_graph(outgoing_edge_dict)
    cycles = list(nx.simple_cycles(graph))
    dag_graph_from_cycles(graph, cycles, cyclenode_to_path_dict)
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

def dag_graph_from_cycles(graph, cycles, cyclenode_to_path_dict):
    for cycle in cycles:
        n_name = get_cycles_node_name()
        graph.add_node(n_name)
        nodes_in_cycle_set = set(cycle) # avoid self looping
        for node in cycle:
            for edge in graph.in_edges(node):
                if edge[0] not in nodes_in_cycle_set:
                    graph.add_edge(edge[0], n_name)
            for edge in graph.out_edges(node):
                if edge[1] not in nodes_in_cycle_set:
                    graph.add_edge(n_name, edge[1])
        graph.remove_nodes_from(cycle)
        cyclenode_to_path_dict[n_name] = cycle

def add_last_action_taken_seq_chains(root, action_minimized, action_minimized_wo_lat, sym_lookup_dict):
    global act_to_lat_sets_dict # [lat] -> {actions}
    non_cycle_paths, cyclenode_to_path_dict = find_all_paths(act_to_lat_sets_dict)
    for path in non_cycle_paths:
        root.add_child(generate_non_cycle_seq_node(action_minimized, action_minimized_wo_lat, sym_lookup_dict, cyclenode_to_path_dict, path))

def generate_non_cycle_seq_node(action_minimized, action_minimized_wo_lat, sym_lookup_dict, cyclenode_to_path_dict, path):
    top_seq = py_trees.composites.Sequence(name=constants.LAT_SEQ_NAME+ get_node_name_counter())
    lat_action = ""
    for action in path:
        if is_cycle_node(action):
            top_seq.add_child(generate_cycle_seq_node(action_minimized, action_minimized_wo_lat, sym_lookup_dict, cyclenode_to_path_dict[action]))
        elif lat_action == "": # first action in chain    
            if action in action_minimized and type(action_minimized[action]) !=  pyeda.boolalg.expr._One:
                top_seq.add_child(recursive_build(action_minimized[action], sym_lookup_dict))
            top_seq.add_child(generate_action_nodes(action))
        else:
            if action in action_minimized_wo_lat and lat_action in action_minimized_wo_lat[action] and type(action_minimized_wo_lat[action][lat_action]) != pyeda.boolalg.expr._One:
                top_seq.add_child(recursive_build(action_minimized_wo_lat[action][lat_action], sym_lookup_dict))
            top_seq.add_child(generate_action_nodes(action))
        lat_action = action
    return top_seq

def generate_cycle_seq_node(action_minimized, action_minimized_wo_lat, sym_lookup_dict, path):
    top_seq = py_trees.composites.Sequence(name=constants.REPEAT_SEQ_NAME + get_node_name_counter())
    lat_action = ""
    for action in path:
        if len(path) == 1: # self cycle
            lat_action = action
        if lat_action == "": # first action in chain    
            if action in action_minimized and type(action_minimized[action]) !=  pyeda.boolalg.expr._One:
                top_seq.add_child(recursive_build(action_minimized[action], sym_lookup_dict))
            top_seq.add_child(generate_action_nodes(action))
        else:
            if action in action_minimized_wo_lat and lat_action in action_minimized_wo_lat[action] and type(action_minimized_wo_lat[action][lat_action]) !=  pyeda.boolalg.expr._One:
               top_seq.add_child(recursive_build(action_minimized_wo_lat[action][lat_action], sym_lookup_dict))
            top_seq.add_child(generate_action_nodes(action))
        lat_action = action
    return top_seq

def save_tree(tree, filename):
    """Saves generated BehaviorTree to dot, svg, and png files

    Args:
        tree (py_trees.trees.BehaviourTree): BehaviorTree to be saved
        filename (str): full filename with path for tree to be saved to
    """
    py_trees.display.render_dot_tree(tree, name=constants.BEHAVIOR_TREE_XML_FILENAME,
                                     with_blackboard_variables=False, target_directory=filename)

def bt_espresso_mod(dt, feature_names, label_names, _binary_features):
    """Runs modified BT-Espresso algorithm with new reductions

    Args:
        dt (sklearn.DecisionTree): DecisionTree to be turned into BehaviorTree
        feature_names (list[str]): List of features
        label_names (list[str]): List of actions

    Returns:
        py_trees.trees.BehaviourTree: Built BehaviorTree
    """
    global binary_feature_set
    binary_feature_set = _binary_features
    global lat_cond_lookup
    lat_cond_lookup = {} # reset from last run
    global act_to_lat_sets_dict
    act_to_lat_sets_dict = {} # reset from last run

    if max_prune(dt):
        return py_trees.composites.Parallel(name="Decision Tree is Only 1 Level, no behavior tree to be made as the most likley action would always be chosen.")
    
    sym_lookup, action_to_pstring = dt_to_pstring(
        dt, 
        feature_names, 
        label_names)
    action_minimized, action_minimized_wo_lat = minimize_bool_expression(
        sym_lookup, 
        action_to_pstring)
    btree = pstring_to_btree(action_minimized, sym_lookup) 
    add_last_action_taken_seq_chains(btree, action_minimized, action_minimized_wo_lat, sym_lookup)
    return btree
