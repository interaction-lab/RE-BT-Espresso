import argparse
import json
import os
import ntpath
import csv
import pandas as pd

DELIMITER = ','

def fileIsCSV(filename):
	return filename.endswith(".csv") or filename.endswith(".CSV")

def makeModName(folderPath, oldFileName):
	if not os.path.isdir(folderPath): os.mkdir(folderPath)
	fileNameStem = oldFileName.split(".")[0]
	return os.fsdecode(os.path.join(folderPath, fileNameStem + "_normalized.csv"))

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
directory_in_str = json_object["csv_folder_path"]
directory = os.fsencode(directory_in_str)

for file in os.listdir(directory):
	fileName = os.fsdecode(file)
	if fileIsCSV(fileName):

		absolutePath = os.fsdecode(os.path.join(directory, file))
		filenameEdited = makeModName(json_object["normalized_path"], fileName)

		with open(absolutePath) as csvfile, open(filenameEdited, mode='w') as csvfileMod:
			csv_reader = csv.reader(csvfile, delimiter = DELIMITER)
			csv_writer = csv.writer(csvfileMod, delimiter = DELIMITER, quotechar = '"', quoting=csv.QUOTE_MINIMAL)

			totalQueues = []
			for lag_feature in json_object["lag_features"]: totalQueues.append([])

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

combined_path = os.path.join(json_object["normalized_path"], "combined_csv.csv")

if os.path.exists(combined_path): os.remove(combined_path)
combined_csv = pd.concat([pd.read_csv(os.fsdecode(os.path.join(json_object["normalized_path"], f))) for f in os.listdir(json_object["normalized_path"])])
combined_csv.to_csv( os.fsdecode(combined_path), index = False, encoding='utf-8-sig')


