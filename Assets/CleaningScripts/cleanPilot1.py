from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import make_column_transformer
import pandas as pd
import numpy as np
import argparse
import cleanPilotHelpers as tools
import os

le = LabelEncoder()

def getBadRows(filename):
	data = pd.read_csv(filename, usecols = ['MeetsPolicy'])
	return data.index[data['MeetsPolicy'] == False].tolist()

def prepare_data(filename):
	bad_rows = getBadRows(filename)
	# print(bad_rows)
	features_data = pd.read_csv(filename, usecols = tools.critical_features, skiprows = bad_rows)
	features_data.ExerciseSubmissionResult = features_data.ExerciseSubmissionResult.fillna("No Submission")

	column_trans = make_column_transformer((OneHotEncoder(), ['newExercise Start', 'ExerciseSubmissionResult', 'ScaffLeft']), remainder = 'passthrough')
	hotEncoded_data = column_trans.fit_transform(features_data)
	hotEncoded_data = np.delete(hotEncoded_data, [0,5], 1) # Delete first and fifth column

	labels_data = pd.read_csv(filename, usecols = ['Label'], skiprows = bad_rows)
	le.fit(labels_data[['Label']].values.ravel())
	labels_data = np.array(le.transform(labels_data[['Label']].values.ravel()))
	return hotEncoded_data, labels_data

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required = True, help = "CSV file path with Pilot study data")
args = vars(ap.parse_args())
directory_in_str = args["path"]


features_data, labels_data = prepare_data(directory_in_str)
labels_reformatted = []
for label in labels_data: labels_reformatted.append([int(label)])
csv_ready = np.append(features_data, labels_reformatted, axis=1)
np.savetxt(os.fsdecode(os.path.join(os.path.dirname(directory_in_str), "hotEncoded_combined.csv")), csv_ready, fmt="%s", delimiter=",", header = "isNewExercise, Correct, Incorrect, No Submission, ScaffLeft, tw, tsla, KCs, KCt, Label", comments='')