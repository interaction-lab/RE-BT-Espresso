# global imports
import argparse
import sys, os

# relative file paths
sim_folder = "DataSim"
experiments_folder = sim_folder + "/configs/experiments"
bt_pipeline_folder = "BehaviorTreeDev"

# sim imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', sim_folder))

# pipeline imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', bt_pipeline_folder))
from json_manager import JsonManager
import run_pipeline

json_file_path = "config.json"
output_file_path = "output.log"
should_recolor = False

def parse_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--config", required = True, help = "Full path to json config file for pipeline, relative paths work as well")
	ap.add_argument("-r", "--recolor", required = False, action='store_true', help = "Run recoloring of all trees")
	args = vars(ap.parse_args())
	json_file_path = ""
	if "config" in args and args["config"] != None:
		json_file_path = args["config"]
	should_recolor = "recolor" in args and args["recolor"] != None and args['recolor']

	return json_file_path, should_recolor

def main():
	"""Runs the simulator and full pipeline end to end
	'-c, --config' - [optional] Path to json config
	"""
	print("Start Experiments")
	json_file_path, should_recolor = parse_args()
	run_pipeline.run_pipeline(json_file_path, should_recolor)

if __name__ == '__main__':
	main()
