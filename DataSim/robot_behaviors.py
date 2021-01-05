import py_trees as pt

class Check_IsNewExercise(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="new_exercise_dialogue")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="IsNewExercise", access=pt.common.Access.READ)

    def update(self):
        if self.blackboard.IsNewExercise:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class Check_ExerciseSubmissionResult(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="check_exercise_submission_result")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="ExerciseSubmissionResult", access=pt.common.Access.READ)

    def update(self):
        if self.blackboard.ExerciseSubmissionResult:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class Check_ExerciseSubmissionExists(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="check_excercise_submission_exists")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="Submit", access=pt.common.Access.READ)

    def update(self):
        if self.blackboard.Submit:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class Check_KC(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="check_KC")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="KC", access=pt.common.Access.READ)

    def update(self):
        if self.blackboard.KC < 0.5:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE
        

class New_exercise_dialogue(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="new_exercise_dialogue")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def update(self):
        self.blackboard.robot_dialogue = "new_exercise_dialogue"
        return pt.common.Status.SUCCESS

class Correct_submission_dialogue(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="correct_exercise_dialogue")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def update(self):
        self.blackboard.robot_dialogue = "correct_exercise_dialogue"
        return pt.common.Status.SUCCESS

class Incorrect_submission_dialogue(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="correct_exercise_dialogue")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def update(self):
        self.blackboard.robot_dialogue = "incorrect_exercise_dialogue"
        return pt.common.Status.SUCCESS

class Hint_dialogue(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="hint_dialogue")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def update(self):
        self.blackboard.robot_dialogue = "hint_dialogue"
        return pt.common.Status.SUCCESS

class Do_nothing(pt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="hint_dialogue")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def update(self):
        self.blackboard.robot_dialogue = None
        return pt.common.Status.SUCCESS