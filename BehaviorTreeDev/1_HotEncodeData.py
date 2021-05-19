from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import make_column_transformer
import pandas as pd
import numpy as np
import argparse
import os
import json
import csv
import pipeline_constants as constants
from json_manager import JsonManager

OUTPUT_LOG_FILE = "output.log"
CATEGORICAL_NULL_VALUE = "No Entry"

def get_hot_encoded_header(hot_encoder, categorical_features):
	header_list = []
	for index, category in enumerate(hot_encoder.categories_):
		original_column_name = categorical_features[index]
		for column in category:
			header_list.append(original_column_name + "_" + column)
	return header_list

def hot_encode_features(features_data, categorical_features):
	for categorical_feature in categorical_features:
		features_data[categorical_feature].fillna(\
			CATEGORICAL_NULL_VALUE, inplace = True)
		features_data[categorical_feature] = features_data[categorical_feature].astype(str)

	hot_encoder = OneHotEncoder()
	hot_encoder.fit(features_data[categorical_features])
	hot_encoded_array = hot_encoder.transform(\
		features_data[categorical_features]).toarray().astype(bool)
	hot_encoded_header = get_hot_encoded_header(\
		hot_encoder, categorical_features)
	return hot_encoded_array, hot_encoded_header

def encode_label_column(label_column):
	label_encoder = LabelEncoder()
	label_encoder.fit(label_column.values.ravel())
	label_column = np.array(label_encoder.transform(label_column.values.ravel()))

	labels_reformatted = [[int(label)] for label in label_column]
	return label_encoder, labels_reformatted

def process_command_line_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--config", required = True, help = "Full path to json config file, relative paths work as well")
	args = vars(ap.parse_args())
	return args["config"]


def generate_feature_col_dictionary(header_row, feature_list, is_label_indices):
	global add_last_action_taken
	feature_columns = dict()
	for column_name in feature_list:
		# loop over header
		found_column = False
		for i, header_col in enumerate(header_row):
			if header_col == column_name:
				feature_columns[column_name] = i
				found_column = True
				break
		if not found_column:
			raise Exception("Could not find feature column " + column_name)
	if not is_label_indices and add_last_action_taken:
		feature_columns[constants.LAST_ACTION_TAKEN_COLUMN_NAME] = len(feature_columns)
	return feature_columns



def get_header_row(combined_csv_file):
	with open(combined_csv_file, 'r', encoding='utf-8-sig') as f:
	    d_reader = csv.DictReader(f)
	    return d_reader.fieldnames

add_last_action_taken = False
def run_hotencode(json_file_path):
	global add_last_action_taken
	print(f"Hot encoding started using {json_file_path}")
	
	json_manager = JsonManager(json_file_path)
	feature_list = json_manager.get_feature_columns()
	categorical_features = json_manager.get_categorical_features()
	add_last_action_taken = json_manager.get_add_last_action_taken()

	if add_last_action_taken:
		categorical_features.append(constants.LAST_ACTION_TAKEN_COLUMN_NAME)
	binary_features = json_manager.get_binary_features()
	hot_encoded_path = json_manager.get_hot_encoded_path()

	constants.remove_folder_if_exists(\
		constants.HOT_ENCODED_CSV_FOLDER_NAME, hot_encoded_path)

	hot_encoded_folder = constants.add_folder_to_directory(\
		constants.HOT_ENCODED_CSV_FOLDER_NAME, hot_encoded_path)
	hot_encoded_file_path = os.fsdecode(os.path.join(\
		hot_encoded_folder, constants.HOT_ENCODED_CSV_FILENAME))

	normalized_folder = os.fsdecode(os.path.join(\
		json_manager.get_normalized_path(), \
		constants.NORMALIZED_CSV_FOLDER_NAME))

	combined_csv_file = os.fsdecode(os.path.join(\
		normalized_folder, \
		constants.COMBINED_CSV_FILENAME))

	
	feature_columns = generate_feature_col_dictionary(get_header_row(combined_csv_file), feature_list, False)

	features_data = pd.read_csv(combined_csv_file, usecols = feature_columns)


	features_data[binary_features] = features_data[binary_features].fillna(0)
	features_data[binary_features] = features_data[binary_features].astype(bool)
	binary_columns_array = features_data[binary_features].to_numpy()

	# hot encoded features
	hot_encoded_array, hot_encoded_header = hot_encode_features(\
		features_data, categorical_features)

	# remove hot encoded features from features_data dataframe
	features_data = features_data.drop(columns = categorical_features + binary_features)
	features_data_array = features_data.to_numpy()

	# encode labels
	labels_data = pd.read_csv(combined_csv_file, \
		usecols = [constants.LABEL_COLUMN_NAME])
	label_encoder, labels_column_array = encode_label_column(labels_data)

	# add hot_encoded columns, than numerical columns, then encoded labels to one array
	final_csv = np.concatenate(\
		(hot_encoded_array, binary_columns_array, \
			features_data_array, labels_column_array), \
		axis = constants.COLUMN_AXIS)

	# make_formatter_string(hot_encoded_header, numerical_columns, label_column)
	hot_encode_fmt = "%s," * len(hot_encoded_header + binary_features) # format hot encoded columns to binary features
	feature_data_fmt = "%1.3f," * len(features_data.columns) # format numerical columns to doubles
	total_fmt = hot_encode_fmt + feature_data_fmt + "%i" # for label

	final_header = ','.join(str(i) for i in (hot_encoded_header + binary_features + list(features_data.columns)))
	final_header += "," + constants.LABEL_COLUMN_NAME # for label


	np.savetxt(hot_encoded_file_path, final_csv, \
		fmt = total_fmt, \
		header = final_header, \
		delimiter = constants.CSV_DELIMITER, \
		comments='')

	f = open(OUTPUT_LOG_FILE, "w")
	f.write("{}\n".format(total_fmt))
	f.write(str((label_encoder.classes_).tolist()))
	f.close()
	print(f"Hot Encoding finished, results in {hot_encoded_file_path}")

def main():
	json_file_path = process_command_line_args()
	run_hotencode(json_file_path)

if __name__ == '__main__':
	main()

