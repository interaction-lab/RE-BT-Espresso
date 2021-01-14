import py_trees as pt
from robot_behaviors import*
from globals import robot_vars, env_vars

class Robot():
    def __init__(self):
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
            Check_IsNewExercise(),
            New_exercise_dialogue()
        ])

        self.sq_correct_submission_dialogue = pt.composites.Sequence(name="sq_correct_submission_dialogue", children= [
            Check_ExerciseSubmissionExists(),
            Check_ExerciseSubmissionResult(),
            Correct_submission_dialogue()
        ])

        self.sq_incorrect_submission_dialogue = pt.composites.Sequence(name="sq_incorrect_submission_dialogue", children= [
            Check_ExerciseSubmissionExists(),
            pt.decorators.Inverter(name="invert_ExerciseSubmissionResult", child=Check_ExerciseSubmissionResult()),
            Incorrect_submission_dialogue()
        ])

        self.sq_hint_dialogue = pt.composites.Sequence(name="sq_hint_dialogue", children= [
            pt.decorators.Inverter(name="invert_ExerciseSubmissionResult", child=Check_ExerciseSubmissionResult()),
            Check_KC(),
            Hint_dialogue()
        ])

        self.root = pt.composites.Parallel(name="root", policy=pt.common.ParallelPolicy.SuccessOnOne(), children= [
            Do_nothing(),
            self.sq_correct_submission_dialogue,
            self.sq_new_exercise_dialogue,
            self.sq_incorrect_submission_dialogue,
            self.sq_hint_dialogue
        ])

        self.b_tree = pt.trees.BehaviourTree(self.root)