import os
import shutil

NORMALIZED_CSV_FOLDER_NAME = "normalized_CSVs"
COMBINED_CSV_FILENAME = "combined_csv.csv"

LAST_ACTION_TAKEN_COLUMN_NAME = "LAST_ACTION_TAKEN"
LAST_ACTION_TAKEN_COLUMN_NAME_NO_ENTRY = LAST_ACTION_TAKEN_COLUMN_NAME + "_No Entry"

HOT_ENCODED_CSV_FOLDER_NAME = "hotEncoded_CSVs"
HOT_ENCODED_CSV_FILENAME = "hotEncoded_combined.csv"

UPSAMPLED_CSV_FOLDER_NAME = "upsampled_CSVs"
UPSAMPLED_CSV_FILENAME = "upsampled_combined.csv"

PIPELINE_OUTPUT_FOLDER_NAME = "pipeline_output"
PRUNE_FOLDER_NAME = "Pruning"
BEHAVIOR_TREE_XML_FILENAME = "behaviorTree"

CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'

LABEL_COLUMN_NAME = "Label"

COLUMN_AXIS = 1

MULTI_ACTION_PAR_SEL_SEPERATOR = "~||~"

AND = "and"
OR = "or"

ACTION_DIFF_TOLERANCE = 0.3

# Description: creates and adds folder called folder_name to directory: working_directory,
#			   returns path to folder
# ex: folder_name = "normalizedCSVs", working_directory = /path/to/directory
# return: "/path/to/directory/normalizedCSVs"
def add_folder_to_directory(folder_name, working_directory):
	new_directory = os.fsdecode(os.path.join(working_directory, folder_name))
	if not os.path.isdir(new_directory): 
		os.makedirs(new_directory)
	return new_directory


def combine_folder_and_working_dir(folder_name, working_directory):
	if working_directory:
		return os.fsdecode(os.path.join(working_directory, folder_name))
	return folder_name

def does_folder_exist_in_directory(folder_name, working_directory=None):
	potential_directory = combine_folder_and_working_dir(folder_name, working_directory)
	return os.path.isdir(potential_directory), potential_directory

def remove_folder_if_exists(folder_name, working_directory=None):
	dir_exists, dir_path = does_folder_exist_in_directory(\
		folder_name, working_directory)
	if dir_exists:
		print(f"Removing prior directory {dir_path}")
		shutil.rmtree(dir_path)
