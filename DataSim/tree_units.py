import py_trees as pt
import random
import sys
from globals import robot_vars, env_vars
from robot_behaviors import*

'''Tree base class'''
class Tree():
    def __init__(self, p_SenseCorrect, p_ActCorrect):
        self.root = None
        self.p_SenseCorrect = p_SenseCorrect
        self.p_ActCorrect = p_ActCorrect
        self.build_behavior_dict()
        self.setup()
        
    def setup(self):
        self.robot_blackboard = pt.blackboard.Client(name="Robot")
        self.define_tree()
        self.init_read_write_access()
        self.reset_robot_state()
        
    def build_behavior_dict(self):
        self.behavior_dict = {
            "action_1": New_exercise_dialogue(self.p_ActCorrect["New_Exercise_Dialogue"]),
            "action_2": Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"]),
            "action_3": Incorrect_submission_dialogue(self.p_ActCorrect["Incorrect_Submission_Dialogue"]),
            "action_4": Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"]),
            "action_5": Check_KC(self.p_SenseCorrect["Check_KC"]),
            "action_6": Check_ExerciseSubmissionExists(self.p_SenseCorrect["Check_ExerciseSubmissionExists"]),
            "action_7": Check_ExerciseSubmissionResult(self.p_SenseCorrect["Check_ExerciseSubmissionResult"]),
            "action_8": Check_IsNewExercise(self.p_SenseCorrect["Check_IsNewExercise"])
        }

    def init_read_write_access(self):
        for key in robot_vars:
            self.robot_blackboard.register_key(key=key, access=pt.common.Access.WRITE)
        for key in env_vars:
            self.robot_blackboard.register_key(key=key, access=pt.common.Access.READ)
    
    def reset_robot_state(self):
        self.robot_blackboard.robot_dialogue = None

    def define_tree(self):
        pass
        
    def render_tree(self):
        pt.display.render_dot_tree(self.root)
        
        
'''Selector/Sequence/Parallel: basic actions'''
class Tree_Basic(Tree):
    def __init__(self, p_SenseCorrect, p_ActCorrect, type, child_list):
        self.child_list = child_list
        self.type = type
        super().__init__(p_SenseCorrect=p_SenseCorrect, p_ActCorrect=p_ActCorrect)
        
    def define_tree(self):
        if self.type == "selector":
            self.root = pt.composites.Selector(name="selector")
        elif self.type == "sequence":
            self.root = pt.composites.Sequence(name="sequence")
        elif self.type == "parallel":
            self.root = pt.composites.Parallel(name="parallel")
        
        for child in self.child_list:
            if child["inverted"]:
                self.root.add_child(pt.decorators.Inverter(name="inverted_"+child["name"], child=self.behavior_dict[child["name"]]))
            else:
                self.root.add_child(self.behavior_dict[child["name"]])
            
        self.b_tree = pt.trees.BehaviourTree(self.root)

# '''Selector: 3 actions'''
# class Tree_Selector_1(Tree):
#     def __init__(self, p_SenseCorrect, p_ActCorrect):
#         super().__init__(p_SenseCorrect=p_SenseCorrect, p_ActCorrect=p_ActCorrect)
    
#     def define_tree(self):
#         self.child_1_act = New_exercise_dialogue(self.p_ActCorrect["New_Exercise_Dialogue"])
#         self.child_2_act = Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"])
#         self.child_3_act = Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"])
        
#         self.root = pt.composites.Selector(name="selector", children= [
#             self.child_1_act,
#             self.child_2_act,
#             self.child_3_act
#         ])
        
#         self.b_tree = pt.trees.BehaviourTree(self.root)
                
        
# '''Selector: 2 actions, 1 inverted action'''
# class Tree_Selector_2(Tree):
#     def __init__(self, p_SenseCorrect, p_ActCorrect):
#         super().__init__(p_SenseCorrect=p_SenseCorrect, p_ActCorrect=p_ActCorrect)
    
#     def define_tree(self):
#         self.child_1_act = Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"])
#         self.child_2_act = Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"])
#         self.child_3_act = pt.decorators.Inverter(name="invert_ExerciseSubmissionResult", child=Check_ExerciseSubmissionResult(self.p_SenseCorrect["Check_ExerciseSubmissionResult"]))
        
#         self.root = pt.composites.Sequence(name="sequence", children= [
#             self.child_1_act,
#             self.child_2_act,
#             self.child_3_act
#         ])
        
#         self.b_tree = pt.trees.BehaviourTree(self.root)
        
# '''Selector: 1 action, 1 sequence (3 actions)'''

        
# '''Sequence: 3 actions'''
# class Tree_Sequence_1(Tree):
#     def __init__(self, p_SenseCorrect, p_ActCorrect):
#         super().__init__(p_SenseCorrect=p_SenseCorrect, p_ActCorrect=p_ActCorrect)
    
#     def define_tree(self):
#         self.child_1_act = New_exercise_dialogue(self.p_ActCorrect["New_Exercise_Dialogue"])
#         self.child_2_act = Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"])
#         self.child_3_act = Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"])
        
#         self.root = pt.composites.Sequence(name="sequence", children= [
#             self.child_1_act,
#             self.child_2_act,
#             self.child_3_act
#         ])
        
#         self.b_tree = pt.trees.BehaviourTree(self.root)
        
#         #pt.display.render_dot_tree(self.root)
        
        
# '''Sequence: 2 actions, 1 inverted action'''
# class Tree_Sequence_2(Tree):
#     def __init__(self, p_SenseCorrect, p_ActCorrect):
#         super().__init__(p_SenseCorrect=p_SenseCorrect, p_ActCorrect=p_ActCorrect)
    
#     def define_tree(self):
#         self.child_2_act = Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"])
#         self.child_3_act = Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"])
#         self.child_1_act = pt.decorators.Inverter(name="invert_ExerciseSubmissionResult", child=Check_ExerciseSubmissionResult(self.p_SenseCorrect["Check_ExerciseSubmissionResult"]))
        
#         self.root = pt.composites.Sequence(name="sequence", children= [
#             self.child_1_act,
#             self.child_2_act,
#             self.child_3_act
#         ])
        
#         self.b_tree = pt.trees.BehaviourTree(self.root)
        
#         #pt.display.render_dot_tree(self.root)


# '''Parallel: 3 actions'''
# class Tree_Parallel_1(Tree):
#     def __init__(self, p_SenseCorrect, p_ActCorrect):
#         super().__init__(p_SenseCorrect=p_SenseCorrect, p_ActCorrect=p_ActCorrect)
    
#     def define_tree(self):
#         self.child_1_act = New_exercise_dialogue(self.p_ActCorrect["New_Exercise_Dialogue"])
#         self.child_2_act = Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"])
#         self.child_3_act = Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"])
        
#         self.root = pt.composites.Parallel(name="parallel", policy=pt.common.ParallelPolicy.SuccessOnOne(), children= [
#             self.child_1_act,
#             self.child_2_act,
#             self.child_3_act
#         ])
        
#         self.b_tree = pt.trees.BehaviourTree(self.root)
        
#         #pt.display.render_dot_tree(self.root)
        
        
# '''Parallel: 2 actions, 1 inverted action'''
# class Tree_Parallel_2(Tree):
#     def __init__(self, p_SenseCorrect, p_ActCorrect):
#         super().__init__(p_SenseCorrect=p_SenseCorrect, p_ActCorrect=p_ActCorrect)
    
#     def define_tree(self):
#         self.child_2_act = Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"])
#         self.child_3_act = Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"])
#         self.child_1_act = pt.decorators.Inverter(name="invert_ExerciseSubmissionResult", child=Check_ExerciseSubmissionResult(self.p_SenseCorrect["Check_ExerciseSubmissionResult"]))
        
#         self.root = pt.composites.Parallel(name="parallel", policy=pt.common.ParallelPolicy.SuccessOnOne(), children= [
#             self.child_1_act,
#             self.child_2_act,
#             self.child_3_act
#         ])
        
#         self.b_tree = pt.trees.BehaviourTree(self.root)
        
#         #pt.display.render_dot_tree(self.root)