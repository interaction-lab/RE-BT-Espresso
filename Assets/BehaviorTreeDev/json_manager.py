import json
import json_constants as json_elements

JSON_CSV_PATH = "csv_folder_path"
JSON_NORMALIZED_PATH = "normalized_path"
JSON_FEATURE_COLUMNS = "feature_columns"
JSON_LABEL_COLUMNS = "label_columns"
JSON_LAG_FEATURES = "lag_features"

class json_manager:

	v_json_object = None

	def __init__(self, json_file_path):
		self.v_json_object = json.load(open(json_file_path))

	def get_feature_columns(self):
		return self.v_json_object[json_elements.JSON_FEATURE_COLUMNS]

	def get_label_columns(self):
		return self.v_json_object[json_elements.JSON_LABEL_COLUMNS]

	def get_lag_features(self):
		return list(self.v_json_object[json_elements.JSON_LAG_FEATURES])

	def get_csv_path(self):
		return str(self.v_json_object[json_elements.JSON_CSV_PATH])

	def get_normalized_path(self):
		return str(self.v_json_object[json_elements.JSON_NORMALIZED_PATH])

	def get_sliding_window_length(self):
		return int(self.v_json_object[json_elements.JSON_SLIDING_WINDOW_LENGTH])
