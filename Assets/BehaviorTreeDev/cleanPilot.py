import csv
import sys
import argparse
import os
import pandas as pd
import json
import cleanPilotHelpers as tools
import ntpath

folderName = "clean_data_NEW"

def makeModName(path):
	head, tail = ntpath.split(path)
	fileName = tail or ntpath.basename(head)
	start = fileName.split(".")[0]
	pathStart = os.path.dirname(path)
	# print("Path Start: {}".format(pathStart))
	newFolder = os.path.join(pathStart, "clean_data_NEW") # pathStart + "clean_data/"
	if not os.path.exists(newFolder):
		os.mkdir(newFolder)
	return os.fsdecode(os.path.join(newFolder, start + "_mod.csv"))

files_processed = 0
warmUpBuffer = 12
tw = 20

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required = True, help = "Path to the folder with CSV(s)")
args = vars(ap.parse_args())
directory_in_str = args["path"]
directory = os.fsencode(directory_in_str)

for file in os.listdir(directory):
	filename = os.fsdecode(file)
	if filename.endswith(".csv") or filename.endswith(".CSV"): 
		files_processed += 1
		absolutePath = os.fsdecode(os.path.join(directory, file))
		filenameEdited = makeModName(absolutePath)

		with open(absolutePath) as csvfile, open(filenameEdited, mode='w') as csvfileMod:
			csv_reader = csv.reader(csvfile, delimiter = ',')
			next(csv_reader, None) # skip headers
			csv_writer = csv.writer(csvfileMod, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

			# currentExercise = 0
			startingTime = tools.getTime(next(csv_reader, None))
			lastActionTime = 0
			scaffoldLeft = -1
			firstHappy = False
			canContinue = False
			visa = ""
			currentExerciseChange = False

			for row in csv_reader:
				currentExerciseChange = False
				currentExercise = 0
				time = tools.getTime(row)
				if time > (startingTime + warmUpBuffer):
					if row[tools.timeseries_Header.robotKCLevel.value] != "": 
						currentTKC = float(row[tools.timeseries_Header.robotKCLevel.value])
					if row[tools.timeseries_Header.CurExercise.value] != "":
						currentExerciseChange = True
						currentExercise = int(row[tools.timeseries_Header.CurExercise.value])
						scaffoldLeft = tools.scaffSize.get(currentExercise)
					# print("scaffoldLeft: {}".format(scaffoldLeft))
					isThereMoreScaff = scaffoldLeft > 0
					KC = tools.computeKC(row[tools.timeseries_Header.humanMoveZScore.value], row[tools.timeseries_Header.humanCurZScore.value])
					tsla = time - lastActionTime

					#DIALOGUE Label
					if row[tools.timeseries_Header.kuriDialogue.value] != "":
						dialogue = tools.getDialogue(row[tools.timeseries_Header.kuriDialogue.value])
						dialogueType = tools.classifyDialogue(dialogue)
						if dialogueType == 4: scaffoldLeft -= 1
						dialogue = "Dialogue: " + str(dialogueType)
						lastActionTime = time
					else: dialogue = ""

					#VISA Label
					if row[tools.timeseries_Header.robotISA.value] != "":
						visa = "VISA"
						lastActionTime = time
					else: visa = ""

					#PPA Label
					if row[tools.timeseries_Header.kuriPhysicalAction.value] != "":
						PPAdesc = str(row[tools.timeseries_Header.kuriPhysicalAction.value])
						if (not(firstHappy) and PPAdesc == "happy"):
							firstHappy = True
							canContinue = False
							lastActionTime = time
						else: 
							canContinue = True
							ppa = "PPA"
							lastActionTime = time
					else: ppa = ""

					if canContinue:
						if not(currentExerciseChange): currentExerciseChange = ''
						csvRow = [time, visa, currentTKC, row[3], row[4], dialogue, currentExerciseChange, row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], ppa, row[23], row[24], KC, tsla, tw, isThereMoreScaff]
						csv_writer.writerow(csvRow)
				else: scaffoldLeft = tools.scaffSize.get(currentExercise)

modDataFolder = os.path.join(directory_in_str, folderName)
print(os.fsdecode(modDataFolder))

# modDataFolder = os.path.join(directory_in_str, "clean_data_NEW")
# combined_path = os.path.join(modDataFolder, "combined_csv.csv")

# if os.path.exists(combined_path): os.remove(combined_path)

# combined_csv = pd.concat([pd.read_csv(os.fsdecode(os.path.join(modDataFolder, f))) for f in os.listdir(modDataFolder)])
# combined_csv.to_csv( os.fsdecode(combined_path), index=False, encoding='utf-8-sig')
# print(os.fsdecode(combined_path))









