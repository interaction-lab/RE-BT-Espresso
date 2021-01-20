import py_trees as pt
import random
from robot_behaviors import*
from globals import robot_vars, env_vars

class Robot():
    def __init__(self, p_SenseCorrect, p_ActCorrect):
        self.p_SenseCorrect = p_SenseCorrect
        self.p_ActCorrect = p_ActCorrect
        self.setup() 
        
    def setup(self):
        self.robot_blackboard = pt.blackboard.Client(name="Robot")
        self.define_tree()
        self.init_read_write_access()
        self.reset_robot_state()

    def init_read_write_access(self):
        for key in robot_vars:
            self.robot_blackboard.register_key(key=key, access=pt.common.Access.WRITE)
        for key in env_vars:
            self.robot_blackboard.register_key(key=key, access=pt.common.Access.READ)
    
    def reset_robot_state(self):
        self.robot_blackboard.robot_dialogue = None

    def define_tree(self):

        self.sq_new_exercise_dialogue = pt.composites.Sequence(name="sq_new_exercise_dialogue", children= [
            Check_IsNewExercise(self.p_SenseCorrect["Check_IsNewExercise"]),
            New_exercise_dialogue(self.p_ActCorrect["New_Exercise_Dialogue"])
        ])

        self.sq_correct_submission_dialogue = pt.composites.Sequence(name="sq_correct_submission_dialogue", children= [
            Check_ExerciseSubmissionExists(self.p_SenseCorrect["Check_ExerciseSubmissionExists"]),
            Check_ExerciseSubmissionResult(self.p_SenseCorrect["Check_ExerciseSubmissionResult"]),
            Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"])
        ])

        self.sq_incorrect_submission_dialogue = pt.composites.Sequence(name="sq_incorrect_submission_dialogue", children= [
            Check_ExerciseSubmissionExists(self.p_SenseCorrect["Check_ExerciseSubmissionExists"]),
            pt.decorators.Inverter(name="invert_ExerciseSubmissionResult", child=Check_ExerciseSubmissionResult(self.p_SenseCorrect["Check_ExerciseSubmissionResult"])),
            Incorrect_submission_dialogue(self.p_ActCorrect["Incorrect_Submission_Dialogue"])
        ])

        self.sq_hint_dialogue = pt.composites.Sequence(name="sq_hint_dialogue", children= [
            pt.decorators.Inverter(name="invert_ExerciseSubmissionResult", child=Check_ExerciseSubmissionResult(self.p_SenseCorrect["Check_ExerciseSubmissionResult"])),
            Check_KC(self.p_SenseCorrect["Check_KC"]),
            Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"])
        ])

        self.root = pt.composites.Parallel(name="root", policy=pt.common.ParallelPolicy.SuccessOnOne(), children= [
            Do_nothing(),
            self.sq_correct_submission_dialogue,
            self.sq_new_exercise_dialogue,
            self.sq_incorrect_submission_dialogue,
            self.sq_hint_dialogue
        ])

        self.b_tree = pt.trees.BehaviourTree(self.root)
        

        