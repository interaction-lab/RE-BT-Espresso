from collections import Counter
import pandas as pd
import argparse
from imblearn.over_sampling import SVMSMOTE
import numpy as np
import os
import argparse
import json
from json_manager import JsonManager
import pipeline_constants as constants

def process_command_line_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-config", "--configuration", required = True, help = "Path to the configuration file")
	ap.add_argument("-outputLog", "--outputLogFile", required = True, help = "Path to log file")
	args = vars(ap.parse_args())
	return args["configuration"], args["outputLogFile"]

def main():
	json_file_path, fmt_file_path = process_command_line_args()
	json_manager = JsonManager(json_file_path)

	if json_manager.get_upsample_status() == True:
		upsampled_path = json_manager.get_upsampled_path()
		hot_encoded_folder = os.fsdecode(os.path.join(json_manager.get_hot_encoded_path(), constants.HOT_ENCODED_CSV_FOLDER_NAME))
		hot_encoded_file = os.fsdecode(os.path.join(hot_encoded_folder, constants.HOT_ENCODED_CSV_FILENAME))

		hotEncoded_data = pd.read_csv(hot_encoded_file)
		features_data = pd.read_csv(hot_encoded_file, usecols = list(hotEncoded_data.columns)[:-1]) # everything except label
		labels_data = pd.read_csv(hot_encoded_file, usecols = [list(hotEncoded_data.columns)[-1]]) # label

		sm = SVMSMOTE(random_state = json_manager.get_random_state())
		X_res, y_res = sm.fit_resample(features_data, labels_data)
		csv_ready = np.append(X_res, y_res, axis = constants.COLUMN_AXIS)

		upsampled_folder = constants.add_folder_to_directory(constants.UPSAMPLED_CSV_FOLDER_NAME, upsampled_path)
		upsampled_file_path = os.fsdecode(os.path.join(upsampled_folder, constants.UPSAMPLED_CSV_FILENAME))
		if os.path.exists(upsampled_file_path): 
			os.remove(upsampled_file_path)

		f = open(fmt_file_path, "r")
		fmt = f.readline()
		f.close()

		header = ','.join(str(i) for i in hotEncoded_data.columns)
		np.savetxt(upsampled_file_path, csv_ready, fmt = fmt, delimiter = constants.CSV_DELIMITER, header = header, comments='')

if __name__ == '__main__':
	main()

