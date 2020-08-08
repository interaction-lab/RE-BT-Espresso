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
COLUMN_AXIS = 1

def get_hot_encoded_header(hot_encoder, categorical_features):
	header_list = []
	for index, category in enumerate(hot_encoder.categories_):
		original_column_name = categorical_features[index]
		for column in category:
			header_list.append(original_column_name + "_" + column)
	return header_list

def hot_encode_features(features_data, categorical_features):
	# fill_null_
	for categorical_feature in categorical_features:
		features_data[categorical_feature].fillna(CATEGORICAL_NULL_VALUE, inplace = True)
		features_data[categorical_feature] = features_data[categorical_feature].astype(str)

	hot_encoder = OneHotEncoder()
	hot_encoder.fit(features_data[categorical_features])
	hot_encoded_array = hot_encoder.transform(features_data[categorical_features]).toarray()
	hot_encoded_header = get_hot_encoded_header(hot_encoder, categorical_features)
	return hot_encoded_array, hot_encoded_header

def encode_label_column(label_column):
	label_encoder = LabelEncoder()
	label_encoder.fit(label_column.values.ravel())
	label_column = np.array(label_encoder.transform(label_column.values.ravel()))

	labels_reformatted = [[int(label)] for label in label_column]
	return label_encoder, labels_reformatted

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

	# hot encoded features
	hot_encoded_array, hot_encoded_header = hot_encode_features(features_data, categorical_features)

	# remove hot encoded features from features_data dataframe
	features_data = features_data.drop(columns = categorical_features)
	features_data_array = features_data.to_numpy()

	# encode labels
	labels_data = pd.read_csv(combined_csv_file, usecols = [constants.LABEL_COLUMN_NAME])
	label_encoder, labels_column_array = encode_label_column(labels_data)

	# add hot_encoded columns, than numerical columns, then encoded labels to one array
	final_csv = np.concatenate((hot_encoded_array, features_data_array, labels_column_array), axis = COLUMN_AXIS)

	# make_formatter_string(hot_encoded_header, numerical_columns, label_column)
	
	hot_encode_fmt = "%i," * len(hot_encoded_header) #format hot encoded column to ints
	feature_data_fmt = "%1.3f," * len(features_data.columns)
	total_fmt = hot_encode_fmt + feature_data_fmt + "%i" # for label

	final_header = ','.join(str(i) for i in hot_encoded_header + list(features_data.columns))
	final_header += "," + constants.LABEL_COLUMN_NAME

	if not os.path.isdir(hot_encoded_path): os.mkdir(hot_encoded_path)
	hot_encoded_path = os.fsdecode(os.path.join(hot_encoded_path, constants.HOT_ENCODED_CSV_FILE_NAME))
	if os.path.exists(hot_encoded_path): os.remove(hot_encoded_path)

	np.savetxt(hot_encoded_path, final_csv, fmt = total_fmt, header = final_header, delimiter = constants.CSV_DELIMITER, comments='')

	outputLogFile = "output.log"

	f = open(outputLogFile, "w")
	f.write("{}\n".format(total_fmt))
	f.write(str(list(label_encoder.inverse_transform(range(len(label_encoder.classes_))))))
	f.close()

if __name__ == '__main__':
	main()

