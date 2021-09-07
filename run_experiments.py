# global imports
import argparse
from multiprocessing import process
import sys, os
import glob
import multiprocessing as mp
from joblib import Parallel, delayed

# relative file paths
sim_folder = "DataSim"
experiments_folder = sim_folder + "/configs/experiments"
bt_pipeline_folder = "BehaviorTreeDev"
result_analysis_folder = "ResultAnalysis"

# local imports, uses hacky path additions
# sim imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', sim_folder))
import bt_sim

# pipeline imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', bt_pipeline_folder))
import run_pipeline
import json_manager
from json_manager import JsonManager

# result analysis imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', result_analysis_folder))
import run_results

json_file_path = "config.json"
output_file_path = "output.log"
should_recolor = run_multiprocess = run_original_bt_espresso = False

def parse_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--config", required = False, help = "Name of experiment config json, without this flag it will recurse though all experiments")
	ap.add_argument("-r", "--recolor", required = False, action='store_true', help = "Run recoloring of all trees")
	ap.add_argument("-m", "--multiprocess", required = False, action='store_true', help = "Run experiments in ||")
	ap.add_argument("-k", "--kevin", required = False, action='store_true', help = "Run w original BT-Espresso also")
	args = vars(ap.parse_args())
	json_file_path = None
	if "config" in args and args["config"] != None:
		json_file_path = args["config"]
	should_recolor = "recolor" in args and args["recolor"] != None and args['recolor']
	run_multiprocess = "multiprocess" in args and args["multiprocess"] != None and args['multiprocess']
	run_original_bt_espresso = "kevin" in args and args["kevin"] != None and args['kevin']
	return json_file_path, should_recolor, run_multiprocess, run_original_bt_espresso

def main():
	"""Runs the simulator and full pipeline end to end
	'-c, --config' - [optional] Path to json config
	"""
	print("Start Experiments")
	global experiments_folder
	base_pipeline_config = "DataSim/configs/base_pipeline_config.json" # this should not be moved

	single_experiment_filename, should_recolor, run_multiprocess, run_original_bt_espresso = parse_args()
	if single_experiment_filename:
		run_experiment(base_pipeline_config, experiments_folder + "/" + single_experiment_filename, should_recolor, run_original_bt_espresso)
	else:
		run_all_experiments(base_pipeline_config, should_recolor, run_multiprocess, run_original_bt_espresso)

def run_all_experiments(base_pipeline_config, should_recolor, run_multiprocess, run_original_bt_espresso):
	if run_multiprocess:
		processes = []
		for config_file in glob.glob(experiments_folder + "/*.json"):
			p = mp.Process(target=run_experiment, args=(base_pipeline_config, config_file, should_recolor))
			processes.append(p)
			p.start()
		for process in processes:
			process.join()
	else:
		for config_file in glob.glob(experiments_folder + "/*.json"):
			run_experiment(base_pipeline_config, config_file, should_recolor)
			
	print("Finished all experiments")

def run_experiment(base_pipeline_config, experiment_file, should_recolor, run_original_bt_espresso):
	sim_data_output_path, sim_tree_name = bt_sim.run_sim(experiment_file)	
	pipeline_config_path = write_pipeline_config(base_pipeline_config, sim_data_output_path, sim_data_output_path + "output")
	bt_tree_filepath_list = run_pipeline.run_pipeline(pipeline_config_path, should_recolor, sim_data_output_path + "fmt.log", run_original_bt_espresso)
	simulated_tree_file = sim_data_output_path + sim_tree_name + ".dot"
	bt_tree_filepath_list.insert(0, simulated_tree_file)
	run_results.run_result_list(bt_tree_filepath_list[:-1]) # removes the tree with nothing in it / final prune
	

def write_pipeline_config(base_pipeline_config, sim_data_output_path, output_folder):
	jm = JsonManager(base_pipeline_config)
	jm.set_csv_path(sim_data_output_path)
	jm.set_output_path(output_folder)
	jm.set_normalized_path(output_folder)
	jm.set_upsampled_path(output_folder)
	jm.set_hot_encoded_path(output_folder)

	pipeline_config_path = sim_data_output_path + "pipeline_config.json"
	jm.write_out_json_to_file(pipeline_config_path)
	return pipeline_config_path

if __name__ == '__main__':
	main()
