import pipeline_constants as constants
import py_trees.decorators
import py_trees.display
import numpy as np
from BTBuilderGlobals import *
from pyeda.boolalg.expr import _LITS
from pyeda.inter import *
import re

# Helper
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


# Helper
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

# Helper
def get_key(dictionary, val):
    for key, value in dictionary.items():
        if val == value:
            return key
    return "key doesn't exist"


# Helper
def get_current_var_name():
    global var_cycle_count    
    tmp = "VAR" + str(var_cycle_count)
    var_cycle_count += 1
    return tmp


# Helper
def is_bool_feature(dt, node_index, feature_names):
    global binary_feature_set
    name = feature_names[dt.feature[node_index]]
    return name in binary_feature_set or is_last_action_taken_condition(name) or ("True" in name)


# Helper
def int_to_condition(int_condition):
    return str(_LITS[int_condition])

# Helper
def is_float_key(k_in):
    return "<=" in k_in

# Helper
def get_key_from_float_expr(k_in):
    return k_in.split("<=")[0], float(k_in.split("<=")[1][1:])

# Helper
def get_node_name_counter():
    global node_name_counter
    _ = f"({node_name_counter})"
    node_name_counter += 1
    return _

# Helper
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

# Helper
def contains_latcond(str_rep_cond):
    for key in lat_cond_lookup:
        # (?<!~) is "is not preceded with ~" to avoid inverted conditions 
        # (?!\S) is nothing or whitespace to avoid VAR1 - VAR10 issue
        key_matches = re.findall("(?<!~)" + key + "(?!\S)", str_rep_cond)
        if len(key_matches) > 0:
            return key_matches[0]
    return ""


# Helper
def convert_double_dict_to_expr(dictionary):
    for key1 in dictionary:
        for key2 in dictionary[key1]:
            dictionary[key1][key2] = expr(dictionary[key1][key2])


# Helper
def get_cycles_node_name():
    global cycle_node_counter
    name = constants.CYLCE_NODE + str(cycle_node_counter)
    cycle_node_counter += 1
    return name

# Helper
def is_last_action_taken_condition(condition):
    return constants.LAST_ACTION_TAKEN_COLUMN_NAME in condition and not "No Entry" in condition

# Helper
def remove_all_lat_conditions(final_cond):
    for key in lat_cond_lookup:
        final_cond = re.sub("(?<!~)" + key + "(?!\S)", " 1 " , final_cond)
        final_cond = re.sub("~" + key + "(?!\S)", " 1 ", final_cond)
    return final_cond

# Tree
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

# Tree
def max_prune(dt):
    return is_leaf_node(dt, 0)

# Tree
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
 
 # Tree

# Tree
def cleaned_action_behavior(action):
    return py_trees.behaviours.Success(
        name=constants.ACTION_NODE_STR + re.sub('[^A-Za-z0-9]+', '', action))

# Tree
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


# Tree
def save_tree(tree, filename):
    """Saves generated BehaviorTree to dot, svg, and png files

    Args:
        tree (py_trees.trees.BehaviourTree): BehaviorTree to be saved
        filename (str): full filename with path for tree to be saved to
    """
    py_trees.display.render_dot_tree(tree, name=constants.BEHAVIOR_TREE_XML_FILENAME,
                                     with_blackboard_variables=False, target_directory=filename)
