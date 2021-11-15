# Globals for Behavior Tree Builder with Descriptions

# [variable_symbol] -> condition
lat_cond_lookup = dict()
# [lat_action] -> prior action
act_to_lat_sets_dict = dict() 
# set of all binary features
binary_feature_set = set()
# Counter for number of variables processed, used for unique naming
var_cycle_count = 0
# Used to give unique names to selector/sequence/inverter nodes to avoid stars
node_name_counter = 0
# Number of cycle nodes, used for unique naming
cycle_node_counter = 0
# [action][lat_action] -> conditions that came with lat minus lat cond
act_lat_conditions_dict = dict() 