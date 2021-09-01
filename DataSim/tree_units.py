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
        
    def render_tree(self, output_path):
        pt.display.render_dot_tree(self.root, target_directory=output_path)
        
class Tree_Basic(Tree):
    def __init__(self, type_, child_list):
        self.child_list = child_list
        self.type_ = type_
        self.writer = None
        self.storage = None
        self.composite_set = {
            "selector",
            "sequence",
            "parallel"
        }
        super().__init__()
        
    def define_tree(self):
        self.recursive_tree_build(self.root, self.type_, self.child_list)
        self.b_tree = pt.trees.BehaviourTree(self.root)
        
    def recursive_tree_build(self, root, type_, c_list):
        composite_node = None

        if type_ == "selector":
            composite_node = pt.composites.Selector(name="selector")
        elif type_ == "sequence":
            composite_node = pt.composites.Sequence(name="sequence")
        elif type_ == "parallel":
            composite_node = pt.composites.Parallel(name="parallel")
        
        if composite_node:
            if root:
                root.add_child(composite_node)
            else:
                self.root = composite_node
            root = composite_node

        for child in c_list:
            if child["inverted"]:
                root.add_child(pt.decorators.Inverter(name="inverted_"+child["name"]))
            if child["type_"] in self.composite_set:
                self.recursive_tree_build(root, child["type_"], child["child_list"])
            elif child["type_"] == "action":
                root.add_child(Action(child["name"], child["p_success"]))
            elif child["type_"] == "condition":
                root.add_child(Condition(child["name"], child["p_success"], child['target_state'], child["threshold"]))
