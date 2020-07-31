from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import make_column_transformer
import pandas as pd
import numpy as np
import argparse
import os
import json

le = LabelEncoder()

def getHotEncodedHeader(hE_object, originalColumnNames):
	headerList = []
	index = 0
	for category in hE_object:
		originalColumn = originalColumnNames[index]
		for column in category:
			headerList.append(originalColumn + "_" + column)
		index += 1
	return headerList

ap = argparse.ArgumentParser()
ap.add_argument("-config", "--configuration", required = True, help = "Path to the configuration file")
args = vars(ap.parse_args())
json_file_path = args["configuration"]
# opening JSON file
json_object = json.load(open(json_file_path))
directory_in_str = json_object["normalized_path"]
directory = os.fsencode(directory_in_str)

fileName = os.fsdecode(os.path.join(directory_in_str, "combined_csv.csv"))

features_data = pd.read_csv(fileName, usecols = json_object["feature_columns"])

for column in json_object["categorical_features"]:
	features_data[column] = features_data[column].astype(str)
	features_data[column].fillna("No Entry", inplace = True)

enc = OneHotEncoder()
enc.fit(features_data[json_object["categorical_features"]])
hE_header = getHotEncodedHeader(enc.categories_, json_object["categorical_features"])

fmt = ""
for i in range(len(hE_header)):
	fmt += "%i,"

hE_array = enc.transform(features_data[json_object["categorical_features"]]).toarray()
features_data = features_data.drop(columns = json_object["categorical_features"])
features_data_columnNames = list(features_data.columns)
for i in range(len(features_data_columnNames)):
	fmt += "%1.3f,"
fmt += "%i"
features_data = features_data.to_numpy()

final_csv = np.append(hE_array, features_data, axis=1)

labels_data = pd.read_csv(fileName, usecols = ['Label'])
le.fit(labels_data[['Label']].values.ravel())
labels_data = np.array(le.transform(labels_data[['Label']].values.ravel()))

labels_reformatted = []
for label in labels_data: labels_reformatted.append([int(label)])

final_csv = np.append(final_csv, labels_reformatted, axis=1)

final_Header = ""
for element in hE_header:
	final_Header += element + ","
for element in features_data_columnNames:
	final_Header += element + ","
final_Header += "Label"


if not os.path.isdir(json_object["hotEncoded_path"]): os.mkdir(json_object["hotEncoded_path"])
hot_encoded_path = os.path.join(json_object["hotEncoded_path"], "hotEncoded_combined.csv")
if os.path.exists(hot_encoded_path): os.remove(hot_encoded_path)

np.savetxt(os.fsdecode(hot_encoded_path), final_csv, fmt=fmt, header = final_Header, delimiter=",", comments='')


outputLogFile = "output.log"

f = open(outputLogFile, "w")
f.write("{}\n".format(fmt))
f.write(str(list(le.inverse_transform(range(len(le.classes_))))))
f.close()