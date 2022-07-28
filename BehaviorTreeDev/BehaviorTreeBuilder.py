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

#new imports
from sympy import*
import re
from pyeda.inter import *

def re_bt_espresso(dt, feature_names, label_names, _binary_features, run_orginal_bt_espresso=False, run_with_gfactor=False):
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
    lat_cond_lookup = {}  # reset from last run
    global act_to_lat_sets_dict
    act_to_lat_sets_dict = {}  # reset from last run

    if run_orginal_bt_espresso:
        constants.ACTION_DIFF_TOLERANCE["val"] = 0

    if max_prune(dt):
        return py_trees.composites.Parallel(name="Decision Tree is Only 1 Level, no behavior tree to be made as the most likley action would always be chosen.")

    sym_lookup, action_to_pstring = dt_to_pstring(
        dt,
        feature_names,
        label_names)
    action_minimized, action_minimized_wo_lat = minimize_bool_expression(
        sym_lookup,
        action_to_pstring,
        run_orginal_bt_espresso,
        run_with_gfactor)
    btree = pstring_to_btree(action_minimized, sym_lookup)
    global cur_prune_num
    if not run_orginal_bt_espresso:
        add_last_action_taken_seq_chains(
            btree, action_minimized, action_minimized_wo_lat, sym_lookup)
    return btree


def dt_to_pstring_recursive(dt, node_index, current_pstring, sym_lookup, action_to_pstring, feature_names, label_names):
    if is_leaf_node(dt, node_index):
        process_leaf_node(dt, node_index, label_names,
                          action_to_pstring, current_pstring)
    else:
        process_non_leaf_node(dt, node_index, feature_names, sym_lookup,
                              current_pstring, action_to_pstring, label_names)


def dt_to_pstring(dt, feature_names, label_names):
    sym_lookup = {}
    action_to_pstring = {}
    dt_to_pstring_recursive(dt, 0, "", sym_lookup,
                            action_to_pstring, feature_names, label_names)
    return sym_lookup, action_to_pstring


def pstring_to_btree(action_dict, sym_lookup_dict):
    root = py_trees.composites.Parallel(name="|| Root")

    for action in action_dict:
        root.add_child(create_action_seq_node(
            action, action_dict, sym_lookup_dict))
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

    build_last_action_taken_dict(
        false_rule, false_letter)  # uses jank from above

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
        action += str(label_names[i])
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
            continue  # deal with empty conditions likely from LAT, still valid
        if type(condition_pstring) == pyeda.boolalg.expr._One:
            pstring_dict[action] = condition_pstring
            continue
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
            continue  # deal with empty conditions likely from LAT, still valid
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
    # check for One
    elif type(pstring_expr) == pyeda.boolalg.expr._One:
        return None
    else:
        new_branch = make_condition_node(
            sym_lookup_dict, pstring_expr.to_ast())

    if recursive:
        for every_operand in pstring_expr.to_ast()[1:]:
            if every_operand[0] == constants.AND or every_operand[0] == constants.OR:
                node = recursive_build(
                    ast2expr(every_operand), sym_lookup_dict)
                if node != None:
                    new_branch.add_child(node)
            else:
                condition_node = make_condition_node(
                    sym_lookup_dict, every_operand)
                if condition_node != None:
                    new_branch.add_child(condition_node)

    return new_branch

# when this is 1, look up var0 kind of thing

# build the variables in sympy
X=150
V = symbols(f"VAR0:{X}")
V_dict = {f"VAR{i}": V[i] for i in range(X)}
v = symbols(f"var0:{X}")
v_dict = {f"var{i}": v[i] for i in range(X)}
v_dict.update(V_dict)

def minimize_bool_expression(sym_lookup, action_to_pstring, run_original_bt_espresso, run_with_gfactor):
    action_minimized = action_min_wo_lat_dict = {}
    espresso_reduction(action_to_pstring, action_minimized)
    if not run_original_bt_espresso:
        action_minimized = remove_float_contained_variables(
            sym_lookup, action_minimized)
        action_min_wo_lat_dict = create_action_min_wo_lat_dict(
            action_minimized)
        action_minimized = factorize_pstring(
            action_minimized)
        ############################
        # run our method:
        if run_with_gfactor:
            our_method_rules = []
            for key, value in action_minimized.items():
                our_method_rules.append(str(value))

            logic_rules = convert_input_to_minimization_into_logic(our_method_rules)
            alg_rules= convert_logic_rules_into_algebraic_expression(logic_rules)
            min_rules_alg = []
            for rule in alg_rules:
                rule= rule.replace("~VAR", "var")
                rule = sympify(rule, locals=v_dict)
                rule_factor = gfactor(rule)
                rule_factor = str(rule_factor).replace("*", " & ").replace("+", "|").replace("var", "~VAR")
                rule_factor = expr(rule_factor)
                min_rules_alg.append(rule_factor)

            action_minimized_copy = dict(action_minimized)
            i=0
            for action in action_minimized_copy:
                action_minimized[action] = min_rules_alg[i]
                i += 1

        ############################ 
         
        dict_copy = dict(action_min_wo_lat_dict)
        for action in dict_copy:
            action_min_wo_lat_dict[action] = factorize_pstring(
                action_min_wo_lat_dict[action])
    return action_minimized, action_min_wo_lat_dict

################### new functions ########################

def convert_input_to_minimization_into_logic(input_to_minimization):
    logic_horn_rules= []
    for rule in input_to_minimization:
        logic_rule=""
        rule=str(rule)
        logic_rule=sympify(str(rule), locals=v_dict)
        logic_horn_rules.append(logic_rule)  
    return logic_horn_rules


def upper_repl(match):
     return match.group(1).upper()

def convert_logic_rules_into_algebraic_expression(Horn_rules_logic):
    algebraic_rules = []
    for logic_expression in Horn_rules_logic:
        logic_expression = str(logic_expression)
        logic_expression = logic_expression.replace("|", "+").replace(" & ", "*")
        logic_expression = re.sub(r'~([a-z])', upper_repl, logic_expression)
        algebraic_rules.append(logic_expression)  
    return algebraic_rules


def gfactor(f):
    d = divisor(f)
    if d == "0":
        return f   
    q, r = divide(f,d)
    #if q has only one term
    if q[0] == 1:
        return f
    if len(str(q[0])) == 1:
        return lf(f, q[0])   
    else:
        q = make_cube_free(q[0])
        d,r =  divide(f,q)
        if cube_free(d[0]):
            if "1" not in q:
                q = gfactor(q)
            #if d!=1:
            d = gfactor(d[0])
            if (r != 0):
                r = gfactor(r)
            return sympify(q, locals=v_dict)*sympify(d, locals=v_dict) + sympify(r, locals=v_dict)
        else:
            c = common_cube(d)
            return lf(f,c)
    
def lf(f, c):
    l = best_literal (f,c)  
    q, r = divide (f,l)
    c = common_cube(q)
    q = gfactor(q[0])
    if (r != 0):
        r = gfactor(r)
    return sympify(l, locals=v_dict)*q + r

def common_cube(f):
    # one addedum
    if "+" not in str(f):
        return f
    cubes =  str(f).replace(" + ","+").replace("[","").replace("]","").split("+")
    c1 = cubes[0]
    c1_var = c1.split("*")
    common_chars_list = []
    for c in range(1, len(cubes)):
        common_chars = ''.join([i for i in c1_var if re.search(i, cubes[c])])
        common_chars_list.append(common_chars)
        if common_chars == [""]:
            return ""
    if len(common_chars) == 0:
        return ""
    elif len(common_chars) == 1:
        common_var = common_chars[0]
    else:
        for i in range(1, len(common_chars),1):
            s1=common_chars[0]
            common_var = ''.join(sorted(set(s1) &
            set(common_chars[i]), key = s1.index)) 
            s1= common_var
    if common_var == "":
            return ""
    common_cube= sympify(common_var, locals=v_dict) 
    return common_cube

def make_cube_free(f):
    if cube_free(f):
        return str(f)
    cube = common_cube(f)
    if str(cube) != "":
        f_cube_free, remainder = divide(f, str(cube))
        return str(f_cube_free).replace("[","").replace("]","")
    else:
        return str(f)
    

def cube_free(f):
    if "+" not in str(f):
        return False
    f_str =  str(f).replace(" ","").replace("+","*").replace("[","").replace("]","")
    literals = f_str.split("*")
    for l in literals:
        q, r = divide(f, l)
        if r == 0:
            return False
    return True

def divide(f, d):
    q, r = reduced(f, [d])
    #Needed for a bug in the sympy library
    r = str(r)
    if "-" in r:
        q= [0]
        r= f
        return q,r
    r = sympify (r, locals=v_dict)
    return q,r

def divisor(f):
    frequencies = {}
    f_str = str(f).replace(" ","").replace("+","*")
    keys = f_str.split("*")
    frequencies = dict()
    for i in keys:
        frequencies[i] = frequencies.get(i, 0) + 1
    most_common_literal = max(frequencies, key=frequencies.get)
    if frequencies[most_common_literal]>1:
        return most_common_literal
    else:
        return "0"

def best_literal(f,c):
    frequencies = {}
    f_str = str(f).replace(" ","").replace("+","*")
    keys = f_str.split("*")
    frequencies = dict()
    for i in keys:
        frequencies[i] = frequencies.get(i, 0) + 1
    best_literal = max(frequencies, key=frequencies.get)
    return best_literal

##########################################################

def espresso_reduction(action_to_pstring, action_minimized):
    for action in action_to_pstring:
        if action_to_pstring[action] == "":
            action_minimized[action] = ""
            continue  # no conditions, likely a LAT, continue
        expression = expr(action_to_pstring[action])
        # happens in case of VARX | ~VARX
        if(not expression.is_dnf() or type(expression) == pyeda.boolalg.expr._Zero):
            continue
        dnf = expression.to_dnf()
        action_minimized[action] = espresso_exprs(dnf)[0]


def add_last_action_taken_seq_chains(root, action_minimized, action_minimized_wo_lat, sym_lookup_dict):
    global act_to_lat_sets_dict  # [lat] -> {actions}
    non_cycle_paths, cyclenode_to_path_dict = find_all_paths(
        act_to_lat_sets_dict)
    for path in non_cycle_paths:
        root.add_child(generate_non_cycle_seq_node(
            action_minimized, action_minimized_wo_lat, sym_lookup_dict, cyclenode_to_path_dict, path))


def generate_non_cycle_seq_node(action_minimized, action_minimized_wo_lat, sym_lookup_dict, cyclenode_to_path_dict, path):
    top_seq = py_trees.composites.Sequence(
        name=constants.LAT_SEQ_NAME + get_node_name_counter())
    lat_action = ""
    for action in path:
        process_action(action_minimized, action_minimized_wo_lat,
                       sym_lookup_dict, path, top_seq, action, lat_action)
        lat_action = action
    return top_seq


def create_action_seq_node(action, action_dict, sym_lookup_dict):
    if(action not in action_dict or action_dict[action] == ""):
        # empty condition set likely from LAT, still valid, deal and continue
        return generate_action_nodes(action)

    # can be None
    top_conditional_seq_node = recursive_build(
        action_dict[action], sym_lookup_dict)

    final_behavior_node = None

    if not isinstance(top_conditional_seq_node, py_trees.composites.Sequence):
        top_seq_node_addition = py_trees.composites.Sequence(
            name="Sequence")
        if top_conditional_seq_node != None:
            top_seq_node_addition.add_child(top_conditional_seq_node)
        final_behavior_node = top_seq_node_addition
    else:
        final_behavior_node = top_conditional_seq_node

    if final_behavior_node != None:
        final_behavior_node.add_child(generate_action_nodes(action))
    else:
        final_behavior_node = generate_action_nodes(action)

    return final_behavior_node


def generate_cycle_seq_node(action_minimized, action_minimized_wo_lat, sym_lookup_dict, path):
    top_seq = py_trees.composites.Sequence(
        name=constants.REPEAT_SEQ_NAME + get_node_name_counter())
    lat_action = ""
    for action in path:
        if len(path) == 1:  # self cycle
            lat_action = action

        process_action(action_minimized, action_minimized_wo_lat,
                       sym_lookup_dict, path, top_seq, action, lat_action)
        lat_action = action
    return top_seq


def process_action(action_minimized, action_minimized_wo_lat, sym_lookup_dict, path, top_seq, action, lat_action):
    if is_cycle_node(action) and lat_action != action:  # multi cycle but not self cycle
        top_seq.add_child(generate_cycle_seq_node(
            action_minimized, action_minimized_wo_lat, sym_lookup_dict, cyclenode_to_path_dict[action]))
    elif lat_action == "" or lat_action == action:  # first action in chain or self cycle
        if action in action_minimized and type(action_minimized[action]) != pyeda.boolalg.expr._One:
            top_seq.add_child(recursive_build(
                action_minimized[action], sym_lookup_dict))
        top_seq.add_child(generate_action_nodes(action))
    else:
        if action in action_minimized_wo_lat and lat_action in action_minimized_wo_lat[action] and type(action_minimized_wo_lat[action][lat_action]) != pyeda.boolalg.expr._One:
            top_seq.add_child(recursive_build(
                action_minimized_wo_lat[action][lat_action], sym_lookup_dict))
        top_seq.add_child(generate_action_nodes(action))
