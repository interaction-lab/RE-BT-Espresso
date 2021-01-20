import py_trees as pt
import random

'''Sense parent class'''
class Sense(pt.behaviour.Behaviour):
    def __init__(self, name, p_correct):
        self.p_correct = p_correct
        super().__init__(name="")
            
    def update(self):
        if random.random() <= self.p_correct:
            return self.check()
        else:
            return not self.check()
    
    def check(self):
        pass
    
'''Sense child classes'''
class Check_IsNewExercise(Sense):
    def __init__(self, p):
        super().__init__(name="new_exercise_dialogue", p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="IsNewExercise", access=pt.common.Access.READ)
        #self.p_correct = p_correct
        
    def check(self):
        if self.blackboard.IsNewExercise:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class Check_ExerciseSubmissionResult(Sense):
    def __init__(self, p):
        super().__init__(name="check_exercise_submission_result", p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="ExerciseSubmissionResult", access=pt.common.Access.READ)

    def check(self):
        if self.blackboard.ExerciseSubmissionResult:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class Check_ExerciseSubmissionExists(Sense):
    def __init__(self, p):
        super().__init__(name="check_excercise_submission_exists", p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="Submit", access=pt.common.Access.READ)

    def check(self):
        if self.blackboard.Submit:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class Check_KC(Sense):
    def __init__(self, p):
        super().__init__(name="check_KC", p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="KC", access=pt.common.Access.READ)

    def check(self):
        if self.blackboard.KC < 0.5:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

'''Action parent class'''
class Act(pt.behaviour.Behaviour):
    def __init__(self, name, p_correct):
        self.p_correct = p_correct
        super().__init__(name="")
            
    def update(self):
        if random.random() <= self.p_correct:
            return self.do_act()
        else:
            return self.fail_act()
    
    def do_act(self):
        pass
    
    def fail_act(self):
        return pt.common.Status.FAILURE

'''Action child classes'''
class New_exercise_dialogue(Act):
    def __init__(self, p):
        super().__init__(name="new_exercise_dialogue", p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def do_act(self):
        self.blackboard.robot_dialogue = "new_exercise_dialogue"
        return pt.common.Status.SUCCESS

class Correct_submission_dialogue(Act):
    def __init__(self, p):
        super().__init__(name="correct_exercise_dialogue", p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def do_act(self):
        self.blackboard.robot_dialogue = "correct_exercise_dialogue"
        return pt.common.Status.SUCCESS

class Incorrect_submission_dialogue(Act):
    def __init__(self, p):
        super().__init__(name="correct_exercise_dialogue", p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def do_act(self):
        self.blackboard.robot_dialogue = "incorrect_exercise_dialogue"
        return pt.common.Status.SUCCESS

class Hint_dialogue(Act):
    def __init__(self, p):
        super().__init__(name="hint_dialogue", p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_dialogue", access=pt.common.Access.WRITE)

    def do_act(self):
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