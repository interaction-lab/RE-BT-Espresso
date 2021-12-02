import py_trees.decorators
import py_trees.display
import pyeda
from pyeda.inter import *
from pyeda.boolalg.expr import _LITS
import pipeline_constants as constants
from BTBuilderGlobals import *
from BTBuilderHelpers import *
from BTBuilderLAT import *
from BTBuilderData import *

def re_bt_espresso(dt, feature_names, label_names, _binary_features, run_orginal_bt_espresso=False):
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
        action_to_pstring,
        run_orginal_bt_espresso)
    btree = pstring_to_btree(action_minimized, sym_lookup)
    
    if not run_orginal_bt_espresso:
        add_last_action_taken_seq_chains(btree, action_minimized, action_minimized_wo_lat, sym_lookup)
    return btree

def dt_to_pstring_recursive(dt, node_index, current_pstring, sym_lookup, action_to_pstring, feature_names, label_names):
    if is_leaf_node(dt, node_index):
        process_leaf_node(dt, node_index, label_names, action_to_pstring, current_pstring)
    else:
        process_non_leaf_node(dt, node_index, feature_names, sym_lookup, current_pstring, action_to_pstring, label_names)

def dt_to_pstring(dt, feature_names, label_names):
    sym_lookup = {}
    action_to_pstring = {}
    dt_to_pstring_recursive(dt, 0, "", sym_lookup,
                            action_to_pstring, feature_names, label_names)
    return sym_lookup, action_to_pstring

def pstring_to_btree(action_dict, sym_lookup_dict):
    root = py_trees.composites.Parallel(name="|| Root")
    
    for action in action_dict:
        root.add_child(create_action_seq_node(action, action_dict, sym_lookup_dict))
    return root

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

def minimize_bool_expression(sym_lookup, action_to_pstring, run_original_bt_espresso):
    action_minimized = action_min_wo_lat_dict = {}
    espresso_reduction(action_to_pstring, action_minimized)
    if not run_original_bt_espresso:
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

def generate_cycle_seq_node(action_minimized, action_minimized_wo_lat, sym_lookup_dict, path):
    top_seq = py_trees.composites.Sequence(name=constants.REPEAT_SEQ_NAME + get_node_name_counter())
    lat_action = ""
    for action in path:
        if is_cycle_node(action): # multi cycle
            top_seq.add_child(generate_cycle_seq_node(action_minimized, action_minimized_wo_lat, sym_lookup_dict, cyclenode_to_path_dict[action]))
        else:
            process_action(action_minimized, action_minimized_wo_lat, sym_lookup_dict, path, top_seq, action, lat_action)
        lat_action = action
    return top_seq

def process_action(action_minimized, action_minimized_wo_lat, sym_lookup_dict, path, top_seq, action, lat_action):
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
