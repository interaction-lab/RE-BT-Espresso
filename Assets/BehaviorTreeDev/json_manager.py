import json

JSON_CSV_PATH = "csv_folder_path"
JSON_NORMALIZED_PATH = "normalized_path"
JSON_HOT_ENCODED_PATH = "hotEncoded_path"
JSON_UPSAMPLED_PATH = "upSampled_path"
JSON_FEATURE_COLUMNS = "feature_columns"
JSON_LABEL_COLUMNS = "label_columns"
JSON_LAG_FEATURES = "lag_features"
JSON_SLIDING_WINDOW_LENGTH = "sliding_window_length"
JSON_CATEGORICAL_FEATURES = "categorical_features"
JSON_RANDOM_STATE = "random_state"
JSON_UPSAMPLE = "upsampling"

class json_manager:

	v_json_object = None

	def __init__(self, json_file_path):
		self.v_json_object = json.load(open(json_file_path))

	def get_feature_columns(self):
		return self.v_json_object[JSON_FEATURE_COLUMNS]

	def get_label_columns(self):
		return self.v_json_object[JSON_LABEL_COLUMNS]

	def get_lag_features(self):
		return list(self.v_json_object[JSON_LAG_FEATURES])

	def get_csv_path(self):
		return str(self.v_json_object[JSON_CSV_PATH])

	def get_normalized_path(self):
		return str(self.v_json_object[JSON_NORMALIZED_PATH])

	def get_upsampled_path(self):
		return str(self.v_json_object[JSON_UPSAMPLED_PATH])

	def get_sliding_window_length(self):
		return int(self.v_json_object[JSON_SLIDING_WINDOW_LENGTH])

	def get_categorical_features(self):
		return list(self.v_json_object[JSON_CATEGORICAL_FEATURES])

	def get_hot_encoded_path(self):
		return str(self.v_json_object[JSON_HOT_ENCODED_PATH])

	def get_random_state(self):
		return self.v_json_object[JSON_RANDOM_STATE]

	def get_upsample_status(self):
		return self.v_json_object[JSON_UPSAMPLE]
