import pipeline_constants as constants
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