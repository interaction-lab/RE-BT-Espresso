from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import make_column_transformer
import pandas as pd
import numpy as np
import argparse
import os
import json
import pipeline_constants as constants
from json_manager import json_manager

CATEGORICAL_NULL_VALUE = "No Entry"

def get_hot_encoded_header(hot_encoder, categorical_features):
	header_list = []
	for index, category in enumerate(hot_encoder.categories_):
		original_column_name = categorical_features[index]
		for column in category:
			header_list.append(original_column_name + "_" + column)
	return header_list

def process_command_line_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-config", "--configuration", required = True, help = "Path to the configuration file")
	args = vars(ap.parse_args())
	return args["configuration"]

def main():
	json_file_path = process_command_line_args()
	JSON_MANAGER = json_manager(json_file_path)
	feature_columns = JSON_MANAGER.get_feature_columns()
	categorical_features = JSON_MANAGER.get_categorical_features()
	hot_encoded_path = JSON_MANAGER.get_hot_encoded_path()

	normalized_folder = os.fsdecode(os.path.join(JSON_MANAGER.get_normalized_path(), constants.NORMALIZED_CSV_FOLDER_NAME))
	combined_csv_file = os.fsdecode(os.path.join(normalized_folder, constants.COMBINED_CSV_FILE_NAME))

	features_data = pd.read_csv(combined_csv_file, usecols = feature_columns)

	for feature in categorical_features:
		features_data[feature].fillna(CATEGORICAL_NULL_VALUE, inplace = True)
		features_data[feature] = features_data[feature].astype(str)
		
	hot_encoder = OneHotEncoder()
	hot_encoder.fit(features_data[categorical_features])
	hot_encoded_header = get_hot_encoded_header(hot_encoder, categorical_features)
	hot_encoded_array = hot_encoder.transform(features_data[categorical_features]).toarray()

	features_data = features_data.drop(columns = categorical_features)
	features_data_array = features_data.to_numpy()

	final_csv = np.append(hot_encoded_array, features_data_array, axis = 1)

	le = LabelEncoder()

	labels_data = pd.read_csv(combined_csv_file, usecols = [constants.LABEL_COLUMN_NAME])
	le.fit(labels_data[[constants.LABEL_COLUMN_NAME]].values.ravel())
	labels_data = np.array(le.transform(labels_data[[constants.LABEL_COLUMN_NAME]].values.ravel()))

	labels_reformatted = []
	for label in labels_data: labels_reformatted.append([int(label)])

	final_csv = np.append(final_csv, labels_reformatted, axis=1)

	hot_encode_fmt = "%i," * len(hot_encoded_header) #format hot encoded column to ints
	feature_data_fmt = "%1.3f," * len(list(features_data.columns))
	total_fmt = hot_encode_fmt + feature_data_fmt + "%i" # for label

	final_header = ""
	for element in hot_encoded_header:
		final_header += element + ","
	for element in list(features_data.columns):
		final_header += element + ","
	final_header += constants.LABEL_COLUMN_NAME

	if not os.path.isdir(hot_encoded_path): os.mkdir(hot_encoded_path)
	hot_encoded_path = os.fsdecode(os.path.join(hot_encoded_path, constants.HOT_ENCODED_CSV_FILE_NAME))
	if os.path.exists(hot_encoded_path): os.remove(hot_encoded_path)

	np.savetxt(hot_encoded_path, final_csv, fmt = total_fmt, header = final_header, delimiter = constants.CSV_DELIMITER, comments='')


	outputLogFile = "output.log"

	f = open(outputLogFile, "w")
	f.write("{}\n".format(total_fmt))
	f.write(str(list(le.inverse_transform(range(len(le.classes_))))))
	f.close()

if __name__ == '__main__':
	main()

