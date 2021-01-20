import os

NORMALIZED_CSV_FOLDER_NAME = "normalized_CSVs"
COMBINED_CSV_FILENAME = "combined_csv.csv"

HOT_ENCODED_CSV_FOLDER_NAME = "hotEncoded_CSVs"
HOT_ENCODED_CSV_FILENAME = "hotEncoded_combined.csv"

UPSAMPLED_CSV_FOLDER_NAME = "upsampled_CSVs"
UPSAMPLED_CSV_FILENAME = "upsampled_combined.csv"

PIPELINE_OUTPUT_FOLDER_NAME = "pipeline_output"
PRUNE_FOLDER_NAME = "Pruning"
# BEHAVIOR_TREE_XML_FILENAME = "behaviorTree.xml"
BEHAVIOR_TREE_XML_FILENAME = "behaviorTree"

CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'

LABEL_COLUMN_NAME = "Label"

COLUMN_AXIS = 1

# Description: creates and adds folder called folder_name to directory: working_directory,
#			   returns path to folder
# ex: folder_name = "normalizedCSVs", working_directory = /path/to/directory
# return: "/path/to/directory/normalizedCSVs"
def add_folder_to_directory(folder_name, working_directory):
	new_directory = os.fsdecode(os.path.join(working_directory, folder_name))
	if not os.path.isdir(new_directory): 
		os.makedirs(new_directory)
	return new_directory