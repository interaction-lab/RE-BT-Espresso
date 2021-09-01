# global imports
import argparse
import sys, os

# relative file paths
sim_folder = "DataSim"
experiments_folder = sim_folder + "/configs/experiments"
bt_pipeline_folder = "BehaviorTreeDev"

# local imports, uses hacky path additions
# sim imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', sim_folder))
import bt_sim

# pipeline imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', bt_pipeline_folder))
import run_pipeline
import json_manager
from json_manager import JsonManager

json_file_path = "config.json"
output_file_path = "output.log"
should_recolor = False

def parse_args():
	ap = argparse.ArgumentParser()
	# TODO: make -c be the experiment folder to run or something
	ap.add_argument("-r", "--recolor", required = False, action='store_true', help = "Run recoloring of all trees")
	args = vars(ap.parse_args())
	should_recolor = "recolor" in args and args["recolor"] != None and args['recolor']
	return should_recolor

def main():
	"""Runs the simulator and full pipeline end to end
	'-c, --config' - [optional] Path to json config
	"""
	print("Start Experiments")
	#TODO: will loop folders later
	sim_config = "DataSim/configs/experiments/expr0.json"
	base_pipeline_config = "DataSim/configs/base_pipeline_config.json"

	should_recolor = parse_args()
	sim_data_output_path, tree_name = bt_sim.run_sim(sim_config)	
	pipeline_config_path = write_pipeline_config(base_pipeline_config, sim_data_output_path)
	run_pipeline.run_pipeline(pipeline_config_path, should_recolor)

def write_pipeline_config(base_pipeline_config, sim_data_output_path):
    jm = JsonManager(base_pipeline_config)
    jm.set_csv_path(sim_data_output_path)
    pipeline_config_path = sim_data_output_path + "pipeline_config.json"
    jm.write_out_json_to_file(pipeline_config_path)
    return pipeline_config_path

if __name__ == '__main__':
	main()
