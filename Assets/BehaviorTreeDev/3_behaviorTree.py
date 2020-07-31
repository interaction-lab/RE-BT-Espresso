from sklearn import tree
import graphviz
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import make_column_transformer
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import behaviorTree_Builder as btBuilder
import json

def plotDecisionTree(model, name, header):
	dot_data = tree.export_graphviz(model, out_file = None, feature_names = header) 
	graph = graphviz.Source(dot_data) 
	graph.render(name)

#adds folder to workingDirectory using os module
def addDirectory(workingDirectory, folderName):
	newDirectory = os.fsdecode(os.path.join(workingDirectory, folderName))
	if not os.path.isdir(newDirectory): os.mkdir(newDirectory)
	return newDirectory


ap = argparse.ArgumentParser()
ap.add_argument("-config", "--configuration", required = True, help = "Path to the configuration file")
ap.add_argument("-outputLog", "--outputLogFile", required = True, help = "Path to log file")
args = vars(ap.parse_args())
json_file_path = args["configuration"]
log_file_path = args["outputLogFile"]

log_file = open(log_file_path, "r")
fmt = log_file.readline()
labelEncoding = str(log_file.readline())
# print("labelEncoding: {}".format(labelEncoding))
labelEncoding = eval(labelEncoding)
# print("testing: {}".format(testing))

json_object = json.load(open(json_file_path))
directory_in_str = json_object["upSampled_path"]
directory = os.fsencode(directory_in_str)
fileName = os.path.join(directory_in_str, "upSampled_combined.csv")

upSampled_data = pd.read_csv(fileName)
numCols = len(upSampled_data.columns)
numCols_list = list(range(numCols))

features_data = pd.read_csv(fileName, usecols = numCols_list[:-1])
labels_data = pd.read_csv(fileName, usecols = [numCols_list[-1]])

kFold = json_object["k_fold"]
maxDepth = json_object["treeDepth"]
outputPath = json_object["outputPackage_path"]
outputPath = os.fsdecode(os.path.join(outputPath, "{}_kFold_{}_maxDepth".format(kFold, maxDepth)))

pruningFigureName = "accuracy_vs_alpha.png"

clfs = []
trains_accu = []
test_accu = []
# for j in range(4):
kf = KFold(shuffle = True, n_splits = kFold)
for train_index, test_index in kf.split(features_data):
	X_train, X_test = features_data.iloc[train_index], features_data.iloc[test_index]
	y_train, y_test = labels_data.iloc[train_index], labels_data.iloc[test_index]

	clf = tree.DecisionTreeClassifier(random_state=0, max_depth = maxDepth)
	clf = clf.fit(X_train, y_train)

	trains_accu.append(clf.score(X_train, y_train))
	test_accu.append(clf.score(X_test, y_test))
	clfs.append(clf)

decisionTreeFile = "{}_kFold_{}_maxDepth.txt".format(kFold, maxDepth)
decisionTreePDF = "{}_kFold_{}_maxDepth".format(kFold, maxDepth)

if not os.path.isdir(outputPath): os.mkdir(outputPath)
decisionTreeFile_path = os.path.join(outputPath, decisionTreeFile)
# if os.path.exists(decisionTreeFile_path): 
# 	os.remove(decisionTreeFile_path)

f = open(decisionTreeFile_path, "w")
f.write("Decision Tree with max_depth: {}, and kFold: {}\n".format(maxDepth, kFold))
f.write("	Average train error with {} fold: {}\n".format(kFold, sum(trains_accu)/len(trains_accu)))
f.write("	Average test error with {} fold: {}\n".format(kFold, sum(test_accu)/len(test_accu)))
f.write("	Decision Tree (DOT format) saved to: {}\n".format(decisionTreePDF))
f.write("	Decision Tree (PDF format) saved to: {}.pdf\n".format(decisionTreePDF))
f.write("Check {} for appropriate pruning.\n\n\n".format(pruningFigureName))


clf = tree.DecisionTreeClassifier(random_state = 0, max_depth = maxDepth)
clf = clf.fit(features_data, labels_data)
PDF_path = os.fsdecode(os.path.join(outputPath, decisionTreePDF))
plotDecisionTree(clf, PDF_path, features_data.columns)


clf = tree.DecisionTreeClassifier(max_depth = maxDepth, random_state = 0)
path = clf.cost_complexity_pruning_path(features_data, labels_data)
ccp_alphas, impurities = path.ccp_alphas, path.impurities


pruningPath = addDirectory(outputPath, "Pruning")
clfs = []
train_scores = []
i = 0
for ccp_alpha in ccp_alphas:
	clf = tree.DecisionTreeClassifier(random_state=0, max_depth = maxDepth, ccp_alpha=ccp_alpha)
	clf.fit(features_data, labels_data)
	score = clf.score(features_data, labels_data)

	clfs.append(clf)
	train_scores.append(score)

	newPrunePath = addDirectory(pruningPath, "Pruning_{}".format(i))
	decisionTreePath = os.fsdecode(os.path.join(newPrunePath, "{}_kFold_{}_maxDepth_{}_prune".format(kFold, maxDepth, i)))
	plotDecisionTree(clf, decisionTreePath, features_data.columns)

	decisionTree = clf.tree_
	behaviorTree = btBuilder.BT_ESPRESSO_mod(decisionTree, features_data.columns, labelEncoding)
	behaviorTreePath = os.fsdecode(os.path.join(newPrunePath, "behaviorTree.xml"))
	btBuilder.saveTree(behaviorTree, behaviorTreePath)



	f.write("prune: {} \n".format(i))
	f.write("	ccp_alpha: {}, train score: {}\n".format(ccp_alpha, train_scores[i]))
	f.write("	Decision Tree saved to {}\n".format(decisionTreePath))
	f.write("	Behavior Tree saved to {}\n\n".format(behaviorTreePath))
	f.write("")

	i += 1




fig, ax = plt.subplots()
ax.set_xlabel("alpha")
ax.set_ylabel("accuracy")
ax.set_title("Accuracy vs alpha for training sets")
ax.plot(ccp_alphas, train_scores, marker='o', label="train", drawstyle="steps-post")
# ax.plot(ccp_alphas, test_scores, marker='o', label="test", drawstyle="steps-post")
ax.legend()
graph_path = os.fsdecode(os.path.join(outputPath, pruningFigureName))
plt.savefig(graph_path)

# print("Behavior Tree XML saved to: {}".format(os.fsdecode(os.path.abspath("test.xml"))))

f.close()
