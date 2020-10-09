from sklearn import tree
import graphviz
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import make_column_transformer
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import json
import behaviorTree_Builder as btBuilder
from json_manager import JsonManager
import pipeline_constants as constants

PRUNING_GRAPH_FILENAME = "accuracy_vs_alpha.png"

def plot_decision_tree(decision_tree_model, filename, feature_header):
	dot_data = tree.export_graphviz(decision_tree_model, out_file = None, \
		feature_names = feature_header) 
	graph = graphviz.Source(dot_data) 
	graph.render(filename)

def process_command_line_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-config", "--configuration", \
		required = True, \
		help = "Path to the configuration file")

	ap.add_argument("-outputLog", "--outputLogFile", \
		required = True, \
		help = "Path to log file")

	args = vars(ap.parse_args())
	return args["configuration"], args["outputLogFile"]

def main():
	json_file_path, log_file_path = process_command_line_args()
	json_manager = JsonManager(json_file_path)

	log_file = open(log_file_path, "r")
	fmt = log_file.readline()
	label_encoding = eval(log_file.readline())
	log_file.close()

	supervised_learning_data = None
	if json_manager.get_upsample_status() == True:
		upsampled_folder = os.fsdecode(os.path.join(\
			json_manager.get_upsampled_path(), constants.UPSAMPLED_CSV_FOLDER_NAME))

		supervised_learning_data = os.fsdecode(os.path.join(\
			upsampled_folder, constants.UPSAMPLED_CSV_FILENAME))
	else:
		hot_encoded_folder = os.fsdecode(os.path.join(\
			json_manager.get_hot_encoded_path(), constants.HOT_ENCODED_CSV_FOLDER_NAME))
		supervised_learning_data = os.fsdecode(os.path.join(\
			hot_encoded_folder, constants.HOT_ENCODED_CSV_FILENAME))

	supervised_learning_dataframe = pd.read_csv(supervised_learning_data)
	features_data = pd.read_csv(supervised_learning_data, \
		usecols = list(supervised_learning_dataframe.columns)[:-1])
	labels_data = pd.read_csv(supervised_learning_data, \
		usecols = [list(supervised_learning_dataframe.columns)[-1]])

	kFold = json_manager.get_kfold()
	max_depth = json_manager.get_decision_tree_depth()
	output_folder = constants.add_folder_to_directory(\
		constants.OUTPUT_FOLDER_NAME, json_manager.get_output_path())
	folder_name = "{}_kFold_{}_maxDepth".format(kFold, max_depth)
	output_full_path = constants.add_folder_to_directory(folder_name, output_folder)

	clfs = []
	trains_accu = []
	test_accu = []
	# for j in range(4):
	kf = KFold(shuffle = True, n_splits = kFold)
	for train_index, test_index in kf.split(features_data):
		X_train, X_test = features_data.iloc[train_index], features_data.iloc[test_index]
		y_train, y_test = labels_data.iloc[train_index], labels_data.iloc[test_index]

		clf = tree.DecisionTreeClassifier(random_state = json_manager.get_random_state(), \
			max_depth = max_depth)
		clf = clf.fit(X_train, y_train)

		trains_accu.append(clf.score(X_train, y_train))
		test_accu.append(clf.score(X_test, y_test))
		clfs.append(clf)

	report_file = "{}_kFold_{}_maxDepth.txt".format(kFold, max_depth)
	dot_pdf_header = "{}_kFold_{}_maxDepth".format(kFold, max_depth)

	report_file_path = os.path.join(output_full_path, report_file)
	# if os.path.exists(decisionTreeFile_path): 
	# 	os.remove(decisionTreeFile_path)

	report_file_obj = open(report_file_path, "w")
	report_file_obj.write("Decision Tree with max_depth: {}, and kFold: {}\n".format(\
		max_depth, kFold))
	report_file_obj.write("	Average train error with {} fold: {}\n".format(\
		kFold, sum(trains_accu)/len(trains_accu)))
	report_file_obj.write("	Average test error with {} fold: {}\n".format(\
		kFold, sum(test_accu)/len(test_accu)))
	report_file_obj.write("	Decision Tree (DOT format) saved to: {}\n".format(dot_pdf_header))
	report_file_obj.write("	Decision Tree (PDF format) saved to: {}.pdf\n".format(dot_pdf_header))
	report_file_obj.write("Check {} for appropriate pruning.\n\n\n".format(PRUNING_GRAPH_FILENAME))

	clf = tree.DecisionTreeClassifier(random_state = json_manager.get_random_state(), \
		max_depth = max_depth)
	clf = clf.fit(features_data, labels_data)
	dot_pdf_full_path = os.fsdecode(os.path.join(output_full_path, dot_pdf_header))
	plot_decision_tree(clf, dot_pdf_full_path, features_data.columns)

	prune_path = clf.cost_complexity_pruning_path(features_data, labels_data)
	ccp_alphas, impurities = prune_path.ccp_alphas, prune_path.impurities


	pruning_folder = constants.add_folder_to_directory(\
		constants.PRUNE_FOLDER_NAME, output_full_path)

	clfs = []
	train_scores = []
	for i, ccp_alpha in enumerate(ccp_alphas):
		clf = tree.DecisionTreeClassifier(random_state = json_manager.get_random_state(), \
			max_depth = max_depth, ccp_alpha=ccp_alpha)
		clf.fit(features_data, labels_data)
		score = clf.score(features_data, labels_data)

		clfs.append(clf)
		train_scores.append(score)

		newPrunePath = constants.add_folder_to_directory("Pruning_{}".format(i), pruning_folder)
		decision_tree_path = os.fsdecode(os.path.join(\
			newPrunePath, "{}_kFold_{}_maxDepth_{}_prune".format(kFold, max_depth, i)))
		plot_decision_tree(clf, decision_tree_path, features_data.columns)

		decision_tree_obj = clf.tree_
		behavior_tree_obj = btBuilder.bt_espresso_mod(\
			decision_tree_obj, features_data.columns, label_encoding)

		behaviot_tree_full_path = os.fsdecode(os.path.join(\
			newPrunePath, constants.BEHAVIOR_TREE_XML_FILENAME))

		# btBuilder.save_tree(behavior_tree_obj, behaviot_tree_full_path)
		btBuilder.save_tree(behavior_tree_obj, newPrunePath)

		report_file_obj.write("prune: {} \n".format(i))
		report_file_obj.write("	ccp_alpha: {}, train score: {}\n".format(ccp_alpha, train_scores[i]))
		report_file_obj.write("	Decision Tree saved to {}\n".format(decision_tree_path))
		report_file_obj.write("	Behavior Tree saved to {}\n\n".format(behaviot_tree_full_path))
		report_file_obj.write("")

	fig, ax = plt.subplots()
	ax.set_xlabel("alpha")
	ax.set_ylabel("accuracy")
	ax.set_title("Accuracy vs alpha for training sets")
	ax.plot(ccp_alphas, train_scores, marker='o', label="train", drawstyle="steps-post")
	ax.legend()
	graph_path = os.fsdecode(os.path.join(output_full_path, PRUNING_GRAPH_FILENAME))
	plt.savefig(graph_path)

	report_file_obj.close()

if __name__ == '__main__':
	main()

