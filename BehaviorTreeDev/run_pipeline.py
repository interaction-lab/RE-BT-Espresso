"""Summary

Attributes:
    behaviortree_3 (TYPE): Description
    hotencode_1 (TYPE): Description
    json_file_path (str): Description
    normalize_0 (TYPE): Description
    output_file_path (str): Description
    upsample_2 (TYPE): Description
"""

import argparse
from json_manager import JsonManager

normalize_0 = __import__('0_NormalizeData')
hotencode_1 = __import__('1_HotEncodeData')
upsample_2 = __import__('2_UpsampleData')
behaviortree_3 = __import__('3_LearnAndBuildBT')
color_bt_trees = __import__('color_bt_trees')

DEFAULT_OUTPUT_PATH = "output.log"

def parse_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--config", required = True, help = "Full path to json config file, relative paths work as well")
	ap.add_argument("-r", "--recolor", required = False, action='store_true', help = "Run recoloring of all trees")
	ap.add_argument("-k", "--kevin", required = False, action='store_true', help = "Run w original BT-Espresso also")
	args = vars(ap.parse_args())
	json_file_path = ""
	if "config" in args and args["config"] != None:
		json_file_path = args["config"]

	should_recolor = "recolor" in args and args["recolor"] != None and args['recolor']
	run_original_bt_espresso = "kevin" in args and args["kevin"] != None and args['kevin']
	return json_file_path, should_recolor, run_original_bt_espresso


def run_pipeline(json_file_path, should_recolor, fmt_file_path, run_original_bt_espresso):
	print("Start BTBuilder pipeline")
	json_manager = JsonManager(json_file_path)

	normalize_0.run_normalize(json_file_path)
	hotencode_1.run_hotencode(json_file_path, fmt_file_path)
	upsample_2.run_upsample(json_file_path, fmt_file_path)
	bt_tree_filepath_list = behaviortree_3.run_behaviortree(json_file_path, fmt_file_path, run_original_bt_espresso)

	if should_recolor:
		color_bt_trees.run_color(json_manager.get_output_path())
	
	return bt_tree_filepath_list

def main():
	"""Runs the full pipeline end to end
	'-c, --config' - [optional] Path to json config
	'-r, --recolor' - [optional] runs recoloring when trees are done generating
	"""
	json_file_path, should_recolor, run_original_bt_espresso = parse_args()
	run_pipeline(json_file_path, should_recolor, DEFAULT_OUTPUT_PATH, run_original_bt_espresso)

if __name__ == '__main__':
	main()
