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

normalize_0 = __import__('0_NormalizeData')
hotencode_1 = __import__('1_HotEncodeData')
upsample_2 = __import__('2_UpsampleData')
behaviortree_3 = __import__('3_LearnAndBuildBT')

json_file_path = "config.json"
output_file_path = "output.log"

def parse_args():
	global json_file_path
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--config", required = False, help = "Full path to json config file, relative paths work as well")
	args = vars(ap.parse_args())
	if "config" in args and args["config"] != None:
		json_file_path = args["config"]

def main():
	"""Runs the full pipeline end to end
	'-c, --config' - [optional] Path to json config
	"""
	print("Start")
	parse_args()
	normalize_0.run_normalize(json_file_path)
	hotencode_1.run_hotencode(json_file_path)
	upsample_2.run_upsample(json_file_path, output_file_path)
	behaviortree_3.run_behaviortree(json_file_path, output_file_path)


if __name__ == '__main__':
	main()
