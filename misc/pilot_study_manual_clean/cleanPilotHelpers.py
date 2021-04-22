from enum import Enum
import os
import ntpath

Congratulations = [
				"Well done!", 
				"Good job!", 
				"Great!", 
				"Excellent!", 
				"Very good!"
				]

Encouragement = [
				"You can do this!", 
				"Go ahead!", 
				"Don't give up!", 
				"Keep trying!"
				]

newHeader = [
			'Time', 
			'tw', 
			'tsla', 
			'newExercise Start', 
			'ExerciseSubmissionResult', 
			'humanMoveZScore', 
			'humanCurZScore', 
			'KCs', 
			'KCt', 
			'ScaffLeft', 
			'Label', 
			'MeetsPolicy'
			]

critical_features = [
			'tw', 
			'tsla', 
			'newExercise Start', 
			'ExerciseSubmissionResult', 
			'KCs', 
			'KCt', 
			'ScaffLeft'
			]


scaffSize = { 0:3, 1:3, 2:3, 3:3, 4:2, 5:1, 6:2, 7:0 }

class timeseries_Header(Enum):
	Time = 0
	ExerciseSubmissionResult = 7
	robotKCLevel = 2
	humanMoveZScore = 19
	humanCurZScore = 21
	CurExercise = 6

	kuriDialogue = 5				# Covers Action Space: { * Dialogue (includes goals) }
	kuriPhysicalAction = 22			# Covers Action Space: { Positive Physical Affect }
	robotISA = 1					# Covers Action Space: { Virtual ISA }

def computeKC(movementZ, curiosityZ):
	return 0.5*float(movementZ) + 0.5*float(curiosityZ)

def getDialogue(kuriDialogue):
	splitUp = kuriDialogue.split("T: ")
	return splitUp[-1]

def getTime(row):
	return float(row[timeseries_Header.Time.value])

def updateQueues(row, submitQueue, newExerciseQueue):
	submitQueue.append(str(row[timeseries_Header.ExerciseSubmissionResult.value]))
	newExerciseQueue.append(str(row[timeseries_Header.CurExercise.value]))

	if len(submitQueue) > 5: submitQueue.pop(0)
	if len(newExerciseQueue) > 5: newExerciseQueue.pop(0)

	return submitQueue, newExerciseQueue

def getSubmissionResult(submitList):
	if 'InCorrect' in submitList: return "InCorrect"
	elif 'Correct' in submitList: return "Correct"
	else: return "No Submission"

def isThereNewExercise(newExerciseList):
	for element in newExerciseList:
		if not(element == ''): return True
	return False

# Explain Exercise Goals: 1
# Congratulatory Dialogue: 2
# Encouraging Dialogue: 3
# Scaffolding Dialogue: 4
def classifyDialogue(dialogue):
	if dialogue in Congratulations: return 2
	elif dialogue in Encouragement: return 3
	elif dialogue[:5] == "Goal:": return 1
	else: return 4

def makeModName(path):
	head, tail = ntpath.split(path)
	fileName = tail or ntpath.basename(head)
	start = fileName.split(".")[0]
	pathStart = os.path.dirname(path)
	# print("Path Start: {}".format(pathStart))
	newFolder = os.path.join(pathStart, "clean_data") # pathStart + "clean_data/"
	if not os.path.exists(newFolder):
		os.mkdir(newFolder)
	return os.fsdecode(os.path.join(newFolder, start + "_mod.csv"))


