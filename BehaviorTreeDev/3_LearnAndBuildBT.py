"""Generally runs DTree -> behavior tree, in need of change per #19

Creates decision trees, checks measures, prunes, and converts them to behavior  trees using behaviorTree_Builder

Attributes:
    PRUNING_GRAPH_FILENAME (str): filepath constant for acurracy vs alpha output graph
"""
from sklearn import tree
import graphviz
from sklearn.model_selection import KFold
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import BehaviorTreeBuilder as btBuilder
from BTBuilderGlobals import cur_prune_num
from json_manager import JsonManager
import pipeline_constants as constants
import numpy as np

PRUNING_GRAPH_FILENAME = "accuracy_vs_alpha.png"
RESULTS_TEXT_FILENAME = "results.txt"

def plot_decision_tree(decision_tree_model, filename, feature_header):
	"""Plots decision tree to output folder
	
	Args:
	    decision_tree_model (sklearn.tree._classes.DecisionTreeClassifier): trained decision tree
	    filename (str): full output file path
	    feature_header (sklearn.tree._classes.DecisionTreeClassifier): TODO
	"""
	dot_data = tree.export_graphviz(decision_tree_model, out_file = None, \
		feature_names = feature_header) 
	graph = graphviz.Source(dot_data) 
	graph.render(filename)

def process_command_line_args():
	"""
	Returns:
	    tuple(str, str): Command line args for (config, output) files
	
	"""
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--config", required = True, help = "Full path to json config file, relative paths work as well")
	ap.add_argument("-o", "--outputlog", required = True, help = "Path to log file")
	ap.add_argument("-k", "--kevin", required = False, action='store_true', help = "Run w original BT-Espresso also")
	args = vars(ap.parse_args())
	return args["config"], args["outputlog"], "kevin" in args and args["kevin"] != None and args['kevin']

def run_behaviortree(json_file_path, log_file_path, run_original_bt_espresso):
	"""Summary	
	Args:
	    json_file_path (str): Full filepath to config.json
	    log_file_path (str): Full filepath to output.log file 
	"""

	r = Runner(json_file_path, log_file_path, run_original_bt_espresso)
	return r.run()

class Runner:

	"""Main runner class for this file
	
	Attributes:
	    json_manager (json_manager.JsonManager): JSON Manager for config.json
	    log_file (_io.TextIOWrapper): Log file used for formatting
	"""
	
	def __init__(self, json_file_path, log_file_path, run_original_bt_espresso):
		"""Summary
		
		Args:
		    json_file_path (str): Full filepath to config.json
		    log_file_path (str): Full filepath to output.log file 
		"""
		print(f"BehaviorTree building started using {json_file_path} and {log_file_path}")
		self.json_manager = JsonManager(json_file_path)
		self.log_file = open(log_file_path, "r")
		self.run_original_bt_espresso = run_original_bt_espresso
	
	def get_file_fmt_and_label_encoding(self):
		"""Summary
		
		Returns:
		    tuple(str, list<str>): Tuple containg string output file format and list of label encodings
		"""
		fmt = self.log_file.readline()
		label_encoding = eval(self.log_file.readline())
		self.log_file.close()
		return fmt, label_encoding

	def get_supervised_data_csv_filepath(self):
		"""Returns filepath of data, uses one hot encoded if upsample = false in config.json
		
		Returns:
		    string: filepath to data csv
		"""
		data_folder = os.fsdecode(os.path.join(\
				self.json_manager.get_hot_encoded_path(), constants.HOT_ENCODED_CSV_FOLDER_NAME))
		filename = constants.HOT_ENCODED_CSV_FILENAME

		if self.json_manager.get_upsample_status():
			data_folder = os.fsdecode(os.path.join(\
				self.json_manager.get_upsampled_path(), constants.UPSAMPLED_CSV_FOLDER_NAME))
			filename = constants.UPSAMPLED_CSV_FILENAME

		return os.fsdecode(os.path.join(\
				data_folder, filename))

	def get_output_folder(self, kFold, max_depth):
		path = constants.combine_folder_and_working_dir(constants.PIPELINE_OUTPUT_FOLDER_NAME, self.json_manager.get_output_path())
		return constants.combine_folder_and_working_dir("{}_kFold_{}_maxDepth".format(kFold, max_depth),path)

	def create_output_folder(self, kFold, max_depth):
		output_folder = constants.add_folder_to_directory(\
			constants.PIPELINE_OUTPUT_FOLDER_NAME, self.json_manager.get_output_path())
		folder_name = "{}_kFold_{}_maxDepth".format(kFold, max_depth)
		return constants.add_folder_to_directory(folder_name, output_folder)
	
	def format_float_list_to_precision(self, list_in, precision):
		prec_str = "{0:0." + str(precision) + "f}"
		return [prec_str.format(i) for i in list_in]

	def k_fold_train_decision_tree_w_max_depth(self, num_k_folds, max_depth, output_full_path):

		kf = KFold(shuffle = True, n_splits = num_k_folds)
		# build full tree on all data
		full_tree = tree.DecisionTreeClassifier(random_state = self.json_manager.get_random_state(), \
				max_depth = max_depth).fit(self.features_data, self.labels_data)

		# get set of alphas from cost_complexity_pruning
		prune_path = full_tree.cost_complexity_pruning_path(self.features_data, self.labels_data)
		ccp_alphas, impurities = prune_path.ccp_alphas, prune_path.impurities

		self.train_scores = [0] * len(ccp_alphas)
		self.test_scores = [0] * len(ccp_alphas)

		# split data into train/test
		for train_index, test_index in kf.split(self.features_data):
			X_train, X_test = self.features_data.iloc[train_index], self.features_data.iloc[test_index]
			y_train, y_test = self.labels_data.iloc[train_index], self.labels_data.iloc[test_index]
			
			# create tree on each alpha
			for i, alpha in enumerate(ccp_alphas):
				if alpha < 0: # bug in sklearn I think
					alpha *= -1
				clf = tree.DecisionTreeClassifier(\
					random_state = self.json_manager.get_random_state(), \
					max_depth = max_depth, \
					ccp_alpha=alpha)
				clf = clf.fit(X_train, y_train)
				self.train_scores[i] += clf.score(X_train, y_train) / num_k_folds
				self.test_scores[i] += clf.score(X_test, y_test) / num_k_folds
		return ccp_alphas

	def generate_full_binary_set(self):
		bin_set = self.json_manager.get_binary_features()
		# categrorical
		cat_set = self.json_manager.get_categorical_features()
		

	def run(self):
		"""Reads in data, trains, and reports results
		"""
		kFold = self.json_manager.get_kfold()
		max_depth = self.json_manager.get_decision_tree_depth()

		constants.remove_folder_if_exists(self.get_output_folder(kFold,max_depth))
		print("Building BTs")

		fmt, label_encoding = self.get_file_fmt_and_label_encoding()

		self.supervised_learning_dataframe = pd.read_csv(self.get_supervised_data_csv_filepath())
		self.features_data = self.supervised_learning_dataframe.loc[:, self.supervised_learning_dataframe.columns != constants.LABEL_COLUMN_NAME]
		self.labels_data = self.supervised_learning_dataframe.loc[:, self.supervised_learning_dataframe.columns == constants.LABEL_COLUMN_NAME]


		output_full_path = self.create_output_folder(kFold, max_depth)
		ccp_alphas = self.k_fold_train_decision_tree_w_max_depth(kFold, max_depth, output_full_path)


		report_file = "{}_kFold_{}_maxDepth.txt".format(kFold, max_depth)
		dot_pdf_header = "{}_kFold_{}_maxDepth".format(kFold, max_depth)

		report_file_path = os.path.join(output_full_path, report_file)
		report_file_obj = open(report_file_path, "w")
		report_file_obj.write("Decision Tree with max_depth: {}, and kFold: {}\n".format(\
			max_depth, kFold))
		report_file_obj.write("	Decision Tree (DOT format) saved to: {}\n".format(dot_pdf_header))
		report_file_obj.write("	Decision Tree (PDF format) saved to: {}.pdf\n".format(dot_pdf_header))
		report_file_obj.write("Check {} for appropriate pruning.\n\n\n".format(PRUNING_GRAPH_FILENAME))

		clf = tree.DecisionTreeClassifier(random_state = self.json_manager.get_random_state(), \
			max_depth = max_depth)
		clf = clf.fit(self.features_data, self.labels_data)
		dot_pdf_full_path = os.fsdecode(os.path.join(output_full_path, dot_pdf_header))
		plot_decision_tree(clf, dot_pdf_full_path, self.features_data.columns)

		prune_path = clf.cost_complexity_pruning_path(self.features_data, self.labels_data)
		#ccp_alphas, impurities = prune_path.ccp_alphas, prune_path.impurities

		pruning_folder = constants.add_folder_to_directory(\
			constants.PRUNE_FOLDER_NAME, output_full_path)

		clfs = []
		train_scores = []
		run_alphas = set()
		i = 0
		ccp_alpha_list_copy = ccp_alphas.copy()
		bt_tree_filepath_list = []
		global cur_prune_num
		for ccp_alpha in ccp_alpha_list_copy:
			cur_prune_num["val"] = i
			if ccp_alpha < 0: # bug in sklearn I think
				ccp_alpha *= -1
			if ccp_alpha in run_alphas: # dublicate zero ccp due to low rounding float
				ccp_alphas = np.delete(ccp_alphas, i)
				self.train_scores = np.delete(self.train_scores, i)
				self.test_scores = np.delete(self.test_scores, i)
				continue
			run_alphas.add(ccp_alpha)
			
			clf = tree.DecisionTreeClassifier(random_state = self.json_manager.get_random_state(), \
				max_depth = max_depth, ccp_alpha=ccp_alpha)
			clf.fit(self.features_data, self.labels_data)
			score = clf.score(self.features_data, self.labels_data)

			clfs.append(clf)
			train_scores.append(score)

			newPrunePath = constants.add_folder_to_directory("Pruning_{0}_{1:.6g}".format(i, ccp_alpha), pruning_folder)
			decision_tree_path = os.fsdecode(os.path.join(\
				newPrunePath, "{0}_kFold_{1}_maxDepth_{2}_{3:.6g}_prune".format(kFold, max_depth,i, ccp_alpha)))
			plot_decision_tree(clf, decision_tree_path, self.features_data.columns)

			decision_tree_obj = clf.tree_

			# theoretical split to dump decision trees out to files
			full_binary_set = self.generate_full_binary_set()
			behavior_tree_obj = btBuilder.re_bt_espresso(\
				decision_tree_obj, 
				self.features_data.columns, 
				label_encoding,
				self.json_manager.get_binary_features())

			behavior_tree_full_path = os.fsdecode(os.path.join(\
				newPrunePath, constants.BEHAVIOR_TREE_XML_FILENAME))

			bt_tree_filepath_list.append(newPrunePath + "/" + constants.BEHAVIOR_TREE_XML_FILENAME + ".dot")
			btBuilder.save_tree(behavior_tree_obj, newPrunePath)

			report_file_obj.write("prune: {} \n".format(i))
			report_file_obj.write("	ccp_alpha: {}, train score: {}\n".format(ccp_alpha, train_scores[i]))
			report_file_obj.write("	Decision Tree saved to {}\n".format(decision_tree_path))
			report_file_obj.write("	Behavior Tree saved to {}\n\n".format(behavior_tree_full_path))
			report_file_obj.write("")

			# KEVINS BT ESPRESSO
			if self.run_original_bt_espresso:
				behavior_tree_obj = btBuilder.re_bt_espresso(\
				decision_tree_obj, 
				self.features_data.columns, 
				label_encoding,
				self.json_manager.get_binary_features(),
				True) # run kevins
				
				original_path = constants.add_folder_to_directory("original_bt_espresso", newPrunePath)
				btBuilder.save_tree(behavior_tree_obj, original_path)
				


			i += 1

		fig, ax = plt.subplots()
		ax.set_xlabel("alpha")
		ax.set_ylabel("accuracy")
		ax.set_title("Accuracy vs alpha for Final Tree Prunes (note: uses all data for final training)")
		ax.plot(ccp_alphas, self.train_scores, marker='o', label="train", drawstyle="steps-post")
		ax.plot(ccp_alphas, self.test_scores, marker='x', label="test", drawstyle="steps-post")
		ax.legend()
		graph_path = os.fsdecode(os.path.join(output_full_path, PRUNING_GRAPH_FILENAME))
		plt.savefig(graph_path)

		results_txt_file = open(os.fsdecode(os.path.join(output_full_path, RESULTS_TEXT_FILENAME)), "w")
		alist = ccp_alphas.flatten().tolist()
		acc_diffs = [a_i - b_i for a_i, b_i in zip(self.train_scores, self.test_scores)]
		float_precision = 6
		results_txt_file.write(f"alphas:\t\t{self.format_float_list_to_precision(alist, float_precision)}\n")
		results_txt_file.write(f"train acc:\t{self.format_float_list_to_precision(self.train_scores, float_precision)}\n")
		results_txt_file.write(f"test acc:\t{self.format_float_list_to_precision(self.test_scores, float_precision)}\n")
		results_txt_file.write(f"acc diff:\t{self.format_float_list_to_precision(acc_diffs, float_precision)}\n")
		results_txt_file.close()

		report_file_obj.close()
		print(f"BehaviorTree buidling finished, results in {output_full_path}")
		return bt_tree_filepath_list
		
def main():
	"""Runs the behavior tree via command line arguments
	"""
	json_file_path, fmt_file_path, run_original_bt_espresso = process_command_line_args()
	run_behaviortree(json_file_path, fmt_file_path, run_original_bt_espresso)

if __name__ == '__main__':
	main()
