import argparse
import json
import os
import ntpath
import csv
import pandas as pd
from json_manager import json_manager
# from queue import Queue

CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'

CSV_EXTENSIONS = (".csv", ".CSV")
CSV_NAME_EXTENSION = "_normalized"
NORMALIZED_CSV_FOLDER_NAME = "normalized_CSVs"
LABEL_COLUMN_NAME = "Label"

COMBINED_CSV_FILE_NAME = "combined_csv.csv"

def is_file_CSV(filename):
	return filename.endswith(CSV_EXTENSIONS)

# Description: creates and adds folder called folder_name to directory: working_directory,
#			   returns path to folder
# ex: folder_name = "normalizedCSVs", working_directory = /path/to/directory
# return: "/path/to/directory/normalizedCSVs"
def add_folder_to_directory(folder_name, working_directory):
	new_directory = os.fsdecode(os.path.join(working_directory, folder_name))
	if not os.path.isdir(new_directory): 
		os.makedirs(new_directory)
	return new_directory

# Description: takes parameter original_filename and adds extension to name
# ex: original_filename = "helloWorld.txt", extension = "_addMe"
# return: helloWorld_addMe.txt
def make_modified_filename(original_filename, extension):
	filename_root, filename_ext = os.path.splitext(os.path.basename(original_filename))
	return filename_root + extension + filename_ext

# Description: updates the 2D queue all_lag_queues at index index with the value value
# returns the first thing in the queue that isnt empty
def update_lag_feature_queue(all_lag_queues, index, value):
	current_queue = all_lag_queues[index]
	current_queue.append(value)
	current_queue.pop(0)
	# print("current_queue: {}".format(current_queue))
	for element in current_queue:
		if not(element == '' or element == None): 
			return element
	return ''

def process_command_line_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-config", "--configuration", required = True, help = "Path to the configuration file")
	args = vars(ap.parse_args())
	return args["configuration"]

def main():
	json_file_path = process_command_line_args()
	JSON_MANAGER = json_manager(json_file_path)

	csv_folder = JSON_MANAGER.get_csv_path()
	normalized_folder = JSON_MANAGER.get_normalized_path()
	feature_columns = JSON_MANAGER.get_feature_columns()
	label_columns = JSON_MANAGER.get_label_columns()
	lag_features = JSON_MANAGER.get_lag_features()
	lag_window_length = JSON_MANAGER.get_sliding_window_length()

	destination_path = add_folder_to_directory(NORMALIZED_CSV_FOLDER_NAME, normalized_folder)

	for file in os.listdir(csv_folder):
		complete_file_path = os.fsdecode(os.path.join(csv_folder, file))

		if is_file_CSV(file):
			normalized_filename = make_modified_filename(file, CSV_NAME_EXTENSION)
			normalized_file_path = os.fsdecode(os.path.join(destination_path, normalized_filename))

			current_csv_obj = open(complete_file_path)
			normalized_csv_obj = open(normalized_file_path, mode='w')

			csv_reader = csv.reader(current_csv_obj, delimiter = CSV_DELIMITER)
			csv_writer = csv.writer(normalized_csv_obj, delimiter = CSV_DELIMITER, quotechar = CSV_QUOTECHAR, quoting=csv.QUOTE_MINIMAL)

			all_lag_queues = [[""] * lag_window_length for lag_feature in lag_features]
			
			header_row = list(feature_columns)
			header_row.append(LABEL_COLUMN_NAME)
			csv_writer.writerow(header_row)


			labelIndex = 0
			for timeseries_row in csv_reader:
				label_row_exists = False
				for columnName, columnIndex in label_columns.items():
					if timeseries_row[columnIndex] != "":
						label_row_exists = True
						labelIndex = columnIndex
						break
				if label_row_exists:
					newRow = []
					for columnName, columnIndex in feature_columns.items():
						try: # checking to see if column is a lag feature. If it is, check lag_queue for anything
							index = lag_features.index(columnName)
							laggedFeature = update_lag_feature_queue(all_lag_queues, index, timeseries_row[columnIndex])
							newRow.append(laggedFeature)
						except ValueError: # column in feature columns is not a lag feature, add directly to newRow
							newRow.append(timeseries_row[feature_columns[columnName]])
					newRow.append(timeseries_row[labelIndex])
					csv_writer.writerow(newRow)
				else: 
					for columnIndex, columnName in enumerate(lag_features):
						value = timeseries_row[feature_columns[columnName]]
						update_lag_feature_queue(all_lag_queues, columnIndex, value)

			current_csv_obj.close()
			normalized_csv_obj.close()

	combined_path = os.path.join(destination_path, COMBINED_CSV_FILE_NAME)

	if os.path.exists(combined_path): 
		os.remove(combined_path)
	combined_csv = pd.concat([pd.read_csv(os.fsdecode(os.path.join(destination_path, f))) for f in os.listdir(destination_path)])
	combined_csv.to_csv( os.fsdecode(combined_path), index = False, encoding='utf-8-sig')


if __name__ == '__main__':
	main()
