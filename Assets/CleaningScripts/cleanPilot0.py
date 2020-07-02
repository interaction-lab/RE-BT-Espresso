import csv
import sys
import argparse
import os
import pandas as pd

import cleanPilotHelpers as tools

tw = 20
warmUpBuffer = 12
tw_Buffer = -0.04

files_processed = 0

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required = True, help = "Path to the folder with csv files")
args = vars(ap.parse_args())
directory_in_str = args["path"]
directory = os.fsencode(directory_in_str)

for file in os.listdir(directory):
	filename = os.fsdecode(file)
	if filename.endswith(".csv") or filename.endswith(".CSV"): 
		files_processed += 1
		absolutePath = os.fsdecode(os.path.join(directory, file)) # file.path # os.fsdecode(os.path.abspath(file))
		# print("absolutePath: {}".format(absolutePath))
		filenameEdited = tools.makeModName(absolutePath)

		with open(absolutePath) as csvfile, open(filenameEdited, mode='w') as csvfileMod:
			csv_reader = csv.reader(csvfile, delimiter = ',')
			next(csv_reader, None) # skip headers
			csv_writer = csv.writer(csvfileMod, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			csv_writer.writerow(tools.newHeader)
			
			currentTKC = 0
			currentExercise = 0
			scaffoldLeft = -1
			lastActionTime = 0
			lineCount = 0
			startingTime = tools.getTime(next(csv_reader, None))
			submitQueue = []
			newExerciseQueue = []
			firstData = True
			tsla = -1
			firstHappy = False

			for row in csv_reader:
				example = False
				time = tools.getTime(row)
				if time > (startingTime + warmUpBuffer):
					meetsPolicy = None
					submitQueue, newExerciseQueue = tools.updateQueues(row, submitQueue, newExerciseQueue)

					if row[tools.timeseries_Header.robotKCLevel.value] != "": currentTKC = float(row[tools.timeseries_Header.robotKCLevel.value])
					if row[tools.timeseries_Header.CurExercise.value] != "":
						currentExercise = int(row[tools.timeseries_Header.CurExercise.value])
						scaffoldLeft = tools.scaffSize.get(currentExercise)

					isThereMoreScaff = scaffoldLeft > 0
					KC = tools.computeKC(row[tools.timeseries_Header.humanMoveZScore.value], row[tools.timeseries_Header.humanCurZScore.value])
					tsla = time - lastActionTime
					result = tools.getSubmissionResult(submitQueue)
					newExercise = tools.isThereNewExercise(newExerciseQueue)

					# Dialogue
					if row[tools.timeseries_Header.kuriDialogue.value] != "":
						dialogue = tools.getDialogue(row[tools.timeseries_Header.kuriDialogue.value])
						dialogueType = tools.classifyDialogue(dialogue)
						if dialogueType == 4: 
							scaffoldLeft -= 1
							if result == "InCorrect" and isThereMoreScaff: meetsPolicy = True
							else: meetsPolicy = False
						elif dialogueType == 3:
							if result == "InCorrect" and not(isThereMoreScaff): meetsPolicy = True
							else: meetsPolicy = False
						elif dialogueType == 2:
							if result == "Correct": meetsPolicy = True
							else: meetsPolicy = False
						if dialogueType == 1:
							if newExercise == True: meetsPolicy = True
							else: meetsPolicy = False
						label = "Dialogue: " + str(dialogueType)
						example = True

					# VISA
					elif row[tools.timeseries_Header.robotISA.value] != "":
						label = "VISA" #: " + str(row[Header.robotISA.value])
						example = True

						if KC < currentTKC and tsla >= tw: meetsPolicy = True
						else: meetsPolicy = False

					#PPA
					elif row[tools.timeseries_Header.kuriPhysicalAction.value] != "":
						PPAdesc = str(row[tools.timeseries_Header.kuriPhysicalAction.value])
						if (not(firstHappy) and PPAdesc == "happy"):
							firstHappy = True
							example = False
							lastActionTime = time
						else:
							label = "PPA" #: " + str(row[Header.kuriPhysicalAction.value])
							example = True
							
							if (KC >= currentTKC and tsla >= (tw + tw_Buffer)) or result == "Correct": meetsPolicy = True
							else: meetsPolicy = False

					if example:
						lastActionTime = time
						csvRow = [time, tw, tsla, newExercise, result, row[tools.timeseries_Header.humanMoveZScore.value], row[tools.timeseries_Header.humanCurZScore.value], KC, currentTKC, isThereMoreScaff, label, meetsPolicy]
						csv_writer.writerow(csvRow)

					# reset
					label = ""
					lineCount += 1
				else: scaffoldLeft = tools.scaffSize.get(currentExercise)
					# if row[tools.timeseries_Header.CurExercise.value] != "":
					# 	currentExercise = int(row[tools.timeseries_Header.CurExercise.value])
						
					# 	print("scaffoldLeft: {}".format(scaffoldLeft))
			print("Done with {}. {} lines processed".format(filename, lineCount))

modDataFolder = os.path.join(directory_in_str, "clean_data")
combined_csv = pd.concat([pd.read_csv(os.fsdecode(os.path.join(modDataFolder, f))) for f in os.listdir(modDataFolder)])
combined_csv.to_csv( os.fsdecode(os.path.join(modDataFolder, "combined_csv.csv")), index=False, encoding='utf-8-sig')










