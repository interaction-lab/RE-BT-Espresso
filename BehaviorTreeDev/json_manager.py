import json

JSON_CSV_PATH_KEY = "csv_folder_path"
JSON_NORMALIZED_PATH_KEY = "normalized_path"
JSON_HOT_ENCODED_PATH_KEY = "hotEncoded_path"
JSON_UPSAMPLED_PATH_KEY = "upSampled_path"
JSON_FEATURE_COLUMNS_KEY = "feature_columns"
JSON_LABEL_COLUMNS_KEY = "label_columns"
JSON_LAG_FEATURES_KEY = "lag_features"
JSON_SLIDING_WINDOW_LENGTH_KEY = "sliding_window_length"
JSON_CATEGORICAL_FEATURES_KEY = "categorical_features"
JSON_RANDOM_STATE_KEY = "random_state"
JSON_UPSAMPLE_KEY = "SVMSMOTE_upsampling"
JSON_KFOLD_KEY = "k_fold"
JSON_TREE_DEPTH_KEY = "decision_tree_depth"
JSON_OUTPUT_PATH_KEY = "output_package_path"
JSON_BINARY_FEATURES = "binary_features"
ADD_LAST_ACTION_TAKEN = "add_last_action_taken"

class JsonManager:

	v_json_object = None

	def __init__(self, json_file_path):
		self.v_json_object = json.load(open(json_file_path))

	def write_out_json_to_file(self, output_path):
		with open(output_path, 'w') as outfile:
			json.dump(self.v_json_object, outfile)

	def get_feature_columns(self):
		return self.v_json_object[JSON_FEATURE_COLUMNS_KEY]

	def get_label_columns(self):
		return self.v_json_object[JSON_LABEL_COLUMNS_KEY]

	def get_lag_features(self):
		return list(self.v_json_object[JSON_LAG_FEATURES_KEY])

	def get_csv_path(self):
		return str(self.v_json_object[JSON_CSV_PATH_KEY])
	
	def set_csv_path(self, new_path):
		self.v_json_object[JSON_CSV_PATH_KEY] = new_path

	def get_normalized_path(self):
		return str(self.v_json_object[JSON_NORMALIZED_PATH_KEY])

	def get_upsampled_path(self):
		return str(self.v_json_object[JSON_UPSAMPLED_PATH_KEY])

	def get_sliding_window_length(self):
		return int(self.v_json_object[JSON_SLIDING_WINDOW_LENGTH_KEY])

	def get_categorical_features(self):
		return list(self.v_json_object[JSON_CATEGORICAL_FEATURES_KEY])

	def get_hot_encoded_path(self):
		return str(self.v_json_object[JSON_HOT_ENCODED_PATH_KEY])

	def get_random_state(self):
		return self.v_json_object[JSON_RANDOM_STATE_KEY]

	def get_upsample_status(self):
		return self.v_json_object[JSON_UPSAMPLE_KEY]

	def get_kfold(self):
		return int(self.v_json_object[JSON_KFOLD_KEY])

	def get_decision_tree_depth(self):
		return int(self.v_json_object[JSON_TREE_DEPTH_KEY])

	def get_output_path(self):
		return str(self.v_json_object[JSON_OUTPUT_PATH_KEY])

	def get_binary_features(self):
		return list(self.v_json_object[JSON_BINARY_FEATURES])
	
	def get_add_last_action_taken(self):
		return bool(self.v_json_object[ADD_LAST_ACTION_TAKEN])
