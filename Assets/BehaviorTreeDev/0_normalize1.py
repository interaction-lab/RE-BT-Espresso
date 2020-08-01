import argparse
import json
import os
import ntpath
import csv
import pandas as pd

CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'

CSV_EXTENSIONS = (".csv", ".CSV")
CSV_NAME_EXTENSION = "_normalized"
NORMALIZED_CSV_FOLDER_NAME = "normalized_CSVs"

def is_file_CSV(filename):
	return filename.endswith(CSV_EXTENSIONS)

# Description: creates and adds folder called folder_name to directory: working_directory,
#			   returns path to folder
# ex: folder_name = "normalizedCSVs", working_directory = /path/to/directory
# return: "/path/to/directory/normalizedCSVs"
def add_folder_to_directory(folder_name, working_directory):
	new_directory = os.fsdecode(os.path.join(working_directory, folder_name))
	if not os.path.isdir(new_directory): os.makedirs(new_directory)
	return new_directory

# Description: takes parameter original_filename and adds extension to name
# ex: original_filename = "helloWorld.txt", extension = "_addMe"
# return: helloWorld_addMe.txt
def make_modified_filename(original_filename, extension):
	filename_root, filename_ext = os.path.splitext(os.path.basename(original_filename))
	return filename_root + extension + filename_ext

def updateQueue(json_object, totalQueues, row, columnName):
	index = 0
	for column in json_object["lag_features"]:
		if columnName == column: break
		else: index += 1

	totalQueues[index].append(row[json_object["feature_columns"][columnName]])
	if len(totalQueues[index]) > json_object["sliding_window_length"]: totalQueues[index].pop(0)
	for element in totalQueues[index]:
		if not(element == '' or element == None): return element
	return ''

ap = argparse.ArgumentParser()
ap.add_argument("-config", "--configuration", required = True, help = "Path to the configuration file")
args = vars(ap.parse_args())
json_file_path = args["configuration"]
# opening JSON file
json_object = json.load(open(json_file_path))
csv_folder = json_object["csv_folder_path"]

json_normalized_folder = json_object["normalized_path"]
destination_path = add_folder_to_directory(NORMALIZED_CSV_FOLDER_NAME, json_normalized_folder)

for file in os.listdir(csv_folder):
	complete_file_path = os.fsdecode(os.path.join(csv_folder, file))

	if is_file_CSV(file):
		normalized_filename = make_modified_filename(file, CSV_NAME_EXTENSION)
		normalized_file_path = os.fsdecode(os.path.join(destination_path, normalized_filename))

		current_csv_obj = open(complete_file_path)
		normalized_csv_obj = open(normalized_file_path, mode='w')

		csv_reader = csv.reader(current_csv_obj, delimiter = CSV_DELIMITER)
		csv_writer = csv.writer(normalized_csv_obj, delimiter = CSV_DELIMITER, quotechar = CSV_QUOTECHAR, quoting=csv.QUOTE_MINIMAL)

		totalQueues = [[] for lag_feature in json_object["lag_features"]]
		print("totalQueues: {}".format(totalQueues))

		#Create header for file, followed by one column for 'Label'
		header = []
		for columnName in json_object["feature_columns"]:
			header.append(columnName)
		header.append("Label")
		csv_writer.writerow(header)

		labelIndex = 0
		for row in csv_reader:
			example = False
			for columnName in json_object["label_columns"]:
				if row[json_object["label_columns"][columnName]] != "":
					example = True
					labelIndex = json_object["label_columns"][columnName]
					break
			if example:
				newRow = []
				for columnName in json_object["feature_columns"]:
					#Handle lag features
					if columnName in json_object["lag_features"]:
						laggedFeature = updateQueue(json_object, totalQueues, row, columnName)
						newRow.append(laggedFeature)
					#if not lag feature then add feature to column
					else: newRow.append(row[json_object["feature_columns"][columnName]])
				newRow.append(row[labelIndex])
				csv_writer.writerow(newRow)
			else: 
				for columnName in json_object["lag_features"]:
					updateQueue(json_object, totalQueues, row, columnName)

		current_csv_obj.close()
		normalized_csv_obj.close()

combined_path = os.path.join(destination_path, "combined_csv.csv")

if os.path.exists(combined_path): os.remove(combined_path)
combined_csv = pd.concat([pd.read_csv(os.fsdecode(os.path.join(destination_path, f))) for f in os.listdir(destination_path)])
combined_csv.to_csv( os.fsdecode(combined_path), index = False, encoding='utf-8-sig')


