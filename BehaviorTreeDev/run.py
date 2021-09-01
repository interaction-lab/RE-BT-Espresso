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

json_file_path = "config.json"
output_file_path = "output.log"
should_recolor = False

def parse_args():
	global json_file_path
	global should_recolor

	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--config", required = False, help = "Full path to json config file, relative paths work as well")
	ap.add_argument("-r", "--recolor", required = False, action='store_true', help = "Run recoloring of all trees")
	args = vars(ap.parse_args())
	if "config" in args and args["config"] != None:
		json_file_path = args["config"]

	should_recolor = "recolor" in args and args["recolor"] != None and args['recolor']

def main():
	"""Runs the full pipeline end to end
	'-c, --config' - [optional] Path to json config
	"""
	print("Start")
	parse_args()
	json_manager = JsonManager(json_file_path)

	normalize_0.run_normalize(json_file_path)
	hotencode_1.run_hotencode(json_file_path)
	upsample_2.run_upsample(json_file_path, output_file_path)
	behaviortree_3.run_behaviortree(json_file_path, output_file_path)

	if should_recolor:
		color_bt_trees.run_color(json_manager.get_output_path())


if __name__ == '__main__':
	main()
