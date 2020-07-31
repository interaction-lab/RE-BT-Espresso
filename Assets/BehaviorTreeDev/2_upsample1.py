from collections import Counter
import pandas as pd
import argparse
from imblearn.over_sampling import SVMSMOTE
import numpy as np
import os
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("-config", "--configuration", required = True, help = "Path to the configuration file")
ap.add_argument("-outputLog", "--outputLogFile", required = True, help = "Path to log file")
args = vars(ap.parse_args())
json_file_path = args["configuration"]
fmt_file_path = args["outputLogFile"]
# opening JSON file
json_object = json.load(open(json_file_path))
directory_in_str = json_object["hotEncoded_path"]
directory = os.fsencode(directory_in_str)

fileName = os.fsdecode(os.path.join(directory_in_str, "hotEncoded_combined.csv"))

f = open(fmt_file_path, "r")
fmt = f.readline()
# labelEncoding = input()


hotEncoded_data = pd.read_csv(fileName)
numCols = len(hotEncoded_data.columns)
numCols_list = list(range(numCols))

header = ""
for element in list(hotEncoded_data.columns):
	header += element + ","
header = header[:-1]


features_data = pd.read_csv(fileName, usecols = numCols_list[:-1])
labels_data = pd.read_csv(fileName, usecols = [numCols_list[-1]])

sm = SVMSMOTE(random_state = 0)
X_res, y_res = sm.fit_resample(features_data, labels_data)
csv_ready = np.append(X_res, y_res, axis=1)

if not os.path.isdir(json_object["upSampled_path"]): os.mkdir(json_object["upSampled_path"])
upSampled_path = os.path.join(json_object["upSampled_path"], "upSampled_combined.csv")
if os.path.exists(upSampled_path): os.remove(upSampled_path)


np.savetxt(os.fsdecode(upSampled_path), csv_ready, fmt=fmt, delimiter=",", header = header, comments='')
