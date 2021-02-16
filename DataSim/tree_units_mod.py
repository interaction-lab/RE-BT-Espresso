import py_trees as pt
import random
import sys
from globals import robot_vars, env_vars
from robot_behaviors_mod import*

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
            # "action_1": New_exercise_dialogue(self.p_ActCorrect["New_Exercise_Dialogue"]),
            # "action_2": Correct_submission_dialogue(self.p_ActCorrect["Correct_Submission_Dialogue"]),
            # "action_3": Incorrect_submission_dialogue(self.p_ActCorrect["Incorrect_Submission_Dialogue"]),
            # "action_4": Hint_dialogue(self.p_ActCorrect["Hint_Dialogue"]),
            # "action_5": Check_KC(self.p_SenseCorrect["Check_KC"]),
            # "action_6": Check_ExerciseSubmissionExists(self.p_SenseCorrect["Check_ExerciseSubmissionExists"]),
            # "action_7": Check_ExerciseSubmissionResult(self.p_SenseCorrect["Check_ExerciseSubmissionResult"]),
            # "action_8": Check_IsNewExercise(self.p_SenseCorrect["Check_IsNewExercise"])
        }

    def init_read_write_access(self):
        for key in robot_vars:
            self.robot_blackboard.register_key(key=key, access=pt.common.Access.WRITE)
        for key in env_vars:
            self.robot_blackboard.register_key(key=key, access=pt.common.Access.READ)
    
    def reset_robot_state(self):
        self.robot_blackboard.robot_action = None

    def define_tree(self):
        pass
        
    def render_tree(self):
        pt.display.render_dot_tree(self.root)
        
        
class Tree_Basic(Tree):
    def __init__(self, p_SenseCorrect, p_ActCorrect, type, child_list):
        self.child_list = child_list
        self.type = type
        super().__init__(p_SenseCorrect=p_SenseCorrect, p_ActCorrect=p_ActCorrect)
        
    def define_tree(self):
        self.root = self.recursive_tree_build(self.type, self.child_list)
        self.b_tree = pt.trees.BehaviourTree(self.root)
        
    def recursive_tree_build(self, type, c_list):
        if type == "selector":
            composite = pt.composites.Selector(name="selector")
        elif type == "sequence":
            composite = pt.composites.Sequence(name="sequence")
        elif type == "parallel":
            composite = pt.composites.Parallel(name="parallel")
        
        for child in c_list:
            if child["inverted"]:
                if child["type"] == "action":
                    composite.add_child(pt.decorators.Inverter(name="inverted_"+child["name"], child=Act(child["name"], 0.5)))
                elif child["type"] == "condition":
                    composite.add_child(pt.decorators.Inverter(name="inverted_"+child["name"], child=Condition(child["name"], 0.5)))
                elif child["type"] == "composite":
                    composite.add_child(pt.decorators.Inverter(name="inverted_"+child["name"], child=self.recursive_tree_build(child["name"], child["child_list"])))
            elif child["type"] == "composite":
                composite.add_child(self.recursive_tree_build(child["name"], child["child_list"]))
            elif child["type"] == "action":
                composite.add_child(Act(child["name"], 0.5))
            elif child["type"] == "condition":
                composite.add_child(Check_State(child["name"], 0.5))
        return composite
            
