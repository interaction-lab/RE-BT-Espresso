import py_trees as pt
import random
import sys
from globals import robot_vars, env_vars, student_vars
from robot_behaviors import*

'''Tree base class'''
class Tree():
    def __init__(self):
        self.root = None
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
        for key in student_vars:
            self.robot_blackboard.register_key(key=key, access=pt.common.Access.READ)
    
    def reset_robot_state(self):
        self.robot_blackboard.robot_action = None

    def define_tree(self):
        pass
        
    def render_tree(self):
        pt.display.render_dot_tree(self.root, target_directory=g.global_output_folder + g.config_folder_name)
        
class Tree_Basic(Tree):
    def __init__(self, type, child_list):
        self.child_list = child_list
        self.type = type
        self.writer = None
        self.storage = None
        super().__init__()
        
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
                    composite.add_child(pt.decorators.Inverter(name="inverted_"+child["name"], child=Action(child["name"], child["p_success"])))
                elif child["type"] == "condition":
                    composite.add_child(pt.decorators.Inverter(name="inverted_"+child["name"], child=Condition(child["name"], child["p_success"], child['target_state'], child["threshold"])))
                elif child["type"] == "composite":
                    composite.add_child(pt.decorators.Inverter(name="inverted_"+child["name"], child=self.recursive_tree_build(child["name"], child["child_list"])))
            elif child["type"] == "composite":
                composite.add_child(self.recursive_tree_build(child["name"], child["child_list"]))
            elif child["type"] == "action":
                composite.add_child(Action(child["name"], child["p_success"]))
            elif child["type"] == "condition":
                composite.add_child(Condition(child["name"], child["p_success"], child['target_state'], child["threshold"]))
        return composite
    
    

            
