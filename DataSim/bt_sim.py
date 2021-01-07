import py_trees as pt
import csv
import random
import copy
from robot_behaviors import*

env_vars = {"Time", "CurExercise", "IsNewExercise", "ExerciseSubmissionResult"}
student_vars = {"Submit", "MoveBlock", "KC"}
robot_vars = {"robot_dialogue"}
filename = "simulated_data.csv"


def main():
    print("start")
    pt.logging.level = pt.logging.Level.DEBUG
    pt.blackboard.Blackboard.enable_activity_stream(100)

    w = World()
    r = Robot()
    s = Student()

    with open(filename, mode='w') as csv_file:
        csv_writer = csv.DictWriter(csv_file,\
            fieldnames=pt.blackboard.Blackboard.keys())
        csv_writer.writeheader()

        for t in range(25):
            csv_writer.writerow(pt.blackboard.Blackboard.storage)
            s.update()
            w.update()
            r.b_tree.tick()
            print(w.blackboard)

    print("done")

class World():
    def __init__(self):
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
        if random.random() < 0.5:
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
        self.blackboard.Time += random.randint(0, 10)


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

class Student():
    def __init__(self):
        self.blackboard = pt.blackboard.Client(name="Student")
        self.init_read_write_access()
        self.reset_state()

    def init_read_write_access(self):
        for key in student_vars:
            self.blackboard.register_key(key=key, access=pt.common.Access.WRITE)
        for key in env_vars:
            self.blackboard.register_key(key=key, access=pt.common.Access.READ)

    def reset_state(self):
        self.blackboard.KC = 0
        self.blackboard.Submit = False
        self.blackboard.MoveBlock = False

    def update(self):
        self.blackboard.KC = random.random()
        if random.random() < 0.5:
            self.blackboard.Submit = True
        else:
            self.blackboard.Submit = False
        if random.random() < 0.5:
            self.blackboard.MoveBlock = True
        else:
            self.blackboard.MoveBlock = False
        
if __name__ == '__main__':
    main()