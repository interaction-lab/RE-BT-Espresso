normalize_0 = __import__('0_normalize1')
hotencode_1 = __import__('1_hotEncode1')
upsample_2 = __import__('2_upsample1')
behaviortree_3 = __import__('3_behaviorTree')

json_file_path = "config.json"
output_file_path = "output.log"

def main():
	print("Start")
	print("Normalizing")
	normalize_0.run_normalize(json_file_path)
	print("Data normalized")

	print("Hotencoding")
	hotencode_1.run_hotencode(json_file_path)
	print("Hot encoded")

	print("Upsampling")
	upsample_2.run_upsample(json_file_path, output_file_path)
	print("Upsampled")

	print("Running BT Creator")
	behaviortree_3.run_behaviortree(json_file_path, output_file_path)
	print("DONE, check pipeline_output folder for details")


if __name__ == '__main__':
	main()
