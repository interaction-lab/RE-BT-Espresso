import pyeda
from BehaviorTreeDev.BTBuilderHelpers import contains_latcond, convert_double_dict_to_expr, convert_expr_ast_to_str_rep, get_key_from_float_expr, is_float_key, is_last_action_taken_condition, remove_all_lat_conditions
from BTBuilderGlobals import *
import pipeline_constants as constants
from pyeda.inter import *
from pyeda.boolalg.expr import _LITS

# Data
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

# Data
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

# Data
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

# Data
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

# Data
def build_last_action_taken_dict(condition, cond_symbol):
    global lat_cond_lookup
    if is_last_action_taken_condition(condition) and cond_symbol not in lat_cond_lookup:
        lat_cond_lookup[cond_symbol] = condition.replace(constants.LAST_ACTION_TAKEN_COLUMN_NAME + "_", "")

# Data
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
