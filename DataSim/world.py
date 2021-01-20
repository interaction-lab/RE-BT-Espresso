import py_trees as pt
import random
from globals import*

class World():
    def __init__(self, p_SubmissionCorrect):
        self.p_SubmissionCorrect = p_SubmissionCorrect
        self.setup()
        
    def setup(self):
        self.blackboard = pt.blackboard.Client(name="World")
        self.init_read_write_access()
        self.reset_world_state()

    def init_read_write_access(self):
        for key in env_vars:
            self.blackboard.register_key(key=key, access=pt.common.Access.WRITE)
        for key in robot_vars.union(student_vars):
            self.blackboard.register_key(key=key, access=pt.common.Access.READ)

    def reset_world_state(self):
        self.blackboard.Time = 0
        self.blackboard.CurExercise = 0
        self.blackboard.ExerciseSubmissionResult = None
        self.blackboard.IsNewExercise = False
        self.prevSubmission = None #track submission from past turn

    def update(self):
        self.prevSubmission = self.blackboard.ExerciseSubmissionResult
        if self.submission_exists():
            self.evaluate_submission()
        else:
            self.clear_submission_result()
        self.try_next_exercise()
        self.update_time()

    def submission_exists(self):
        return self.blackboard.Submit

    def evaluate_submission(self):
        if random.random() < self.p_SubmissionCorrect:
            self.blackboard.ExerciseSubmissionResult = True
        else:
            self.blackboard.ExerciseSubmissionResult = False
            
    def clear_submission_result(self):
        self.blackboard.ExerciseSubmissionResult = None

    def try_next_exercise(self):
        if self.prevSubmission:
            self.blackboard.IsNewExercise = True
            self.blackboard.CurExercise += 1
        else:
            self.blackboard.IsNewExercise = False

    def update_time(self):
        self.blackboard.Time += 1