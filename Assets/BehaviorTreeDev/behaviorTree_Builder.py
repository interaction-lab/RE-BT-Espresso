from lxml import etree

def isLeafNode(dt, nodeIndex):
	return (dt.children_left[nodeIndex] == -1 and dt.children_right[nodeIndex] == -1)

def build_rules_rec(dt, nodeIndex, currentBuildPath, totalArray, feature_names):
	if isLeafNode(dt, nodeIndex):
		totalArray.append([dt.value[nodeIndex], currentBuildPath])
		# return totalArray
	else:
		trueRule = feature_names[dt.feature[nodeIndex]] + " <= " + str(dt.threshold[nodeIndex])
		falseRule = feature_names[dt.feature[nodeIndex]] + " > " + str(dt.threshold[nodeIndex])	

		leftPath = currentBuildPath.copy()
		leftPath.append([trueRule])
		build_rules_rec(dt, dt.children_left[nodeIndex], leftPath, totalArray, feature_names)

		rightPath = currentBuildPath.copy()
		rightPath.append([falseRule])
		build_rules_rec(dt, dt.children_right[nodeIndex], rightPath, totalArray, feature_names)

def DT_TO_RULES(dt, feature_names):
	totalArray = []
	build_rules_rec(dt, 0, [], totalArray, feature_names)
	return totalArray

def addChild(parent, child):
	parent.append(child)

def createBehaviorTree():
	frame = etree.Element("root")
	tree = etree.ElementTree(frame)
	frame.set('main_tree_to_execute', 'MainTree')

	mainBehavior = etree.Element("BehaviorTree")
	mainBehavior.set('ID', 'MainTree')
	frame.append(mainBehavior)

	return mainBehavior, tree

def ParallelNode(name, parent):
	parallelNode = etree.Element("Parallel")
	parallelNode.set('name', name)
	addChild(parent, parallelNode)
	return parallelNode

def SequenceNode(name, parent):
	sequenceNode = etree.Element("Sequence")
	sequenceNode.set('name', name)
	addChild(parent, sequenceNode)
	return sequenceNode

def ConditionNode(name, parent):
	condition = etree.Element("Condition")
	condition.set('ID', name)
	condition.set('name', name)
	condition.set('message', "")
	addChild(parent, condition)
	return condition

def ActionNode(name, parent):
	action = etree.Element("Action")
	action.set('ID', name)
	action.set('name', name)
	action.set('message', "")
	addChild(parent, action)
	return action

def FallbackNode(name, parent):
	fallbackNode = etree.Element("Fallback")
	fallbackNode.set('name', name)
	addChild(parent, fallbackNode)
	return fallbackNode

def findMaxIndex(numpyArray):
	index = 0
	maxNum = 0
	incrementer = 0
	for element in numpyArray:
		if element > maxNum:
			maxNum = element
			index = incrementer
		incrementer += 1
	return index

def BT_ESPRESSO_mod(dt, feature_names, label_names):
	rules = DT_TO_RULES(dt, feature_names)
	# print("rules: {}".format(rules))
	mainBehavior, tree = createBehaviorTree()
	root = FallbackNode('root', mainBehavior)

	for rule in rules:
		action = rule[0][0]
		labelIndex = findMaxIndex(action)
		label = label_names[labelIndex]
		newRule = SequenceNode(str(label), root)
		conditions = SequenceNode("Conditions", newRule)
		for decision in rule[1]:
			# print("decision[0]: {}".format(decision[0]))
			conditionPart = ConditionNode(decision[0], conditions)
		# action = rule[0][0]
		# labelIndex = findMaxIndex(action)
		# print("action: {}".format(action))
		# index = action.index(max(action))
		addAction = ActionNode(str(label), newRule)

	return tree

def saveTree(tree, fileName):
	with open (fileName, "wb") as file: tree.write(file, pretty_print = True)

