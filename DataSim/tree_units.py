import py_trees as pt
import random
import sys

from py_trees import composites
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
        
    def render_tree(self, output_path, n_in):
        pt.display.render_dot_tree(self.root, target_directory=output_path, name=n_in)
        
class Tree_Basic(Tree):
    def __init__(self, type_, name, child_list):
        self.child_list = child_list
        self.type_ = type_
        self.writer = None
        self.storage = None
        self.name = name
        self.composite_set = {
            "selector",
            "sequence",
            "parallel",
            "repeater",
            "parsel"
        }
        super().__init__()
        
    def define_tree(self):
        self.build_tree(self.root, self.type_, self.name, self.child_list)
        self.b_tree = pt.trees.BehaviourTree(self.root)
        
    def build_tree(self, root, type_, name_, c_list):
        composite_node = self.create_composite(type_, name_)
        if composite_node:
            root = self.add_composite_to_root(root, composite_node)
        for child in c_list:
            self.add_child_to_root(root, child)


    def add_child_to_root(self, root, child):
        if "inverted" in child and child["inverted"]:
            root.add_child(pt.decorators.Inverter(name="Inverter_"+child["name"]))

        if child["type_"] in self.composite_set:
            self.build_tree(root, child["type_"], child['name'], child["child_list"])
        elif child["type_"] == "action":
            root.add_child(Action(child["name"], child["p_success"]))
        elif child["type_"] == "condition":
            # made name target state for easier matching
            root.add_child(Condition(child["target_state"], child["p_success"], child['target_state'], child["threshold"]))

    def add_composite_to_root(self, root, composite_node):
        if root:
            root.add_child(composite_node)
        else:
            self.root = composite_node
        root = composite_node
        return root

    def create_composite(self, type_, name):
        composite_node = None
        if type_ == "selector":
            composite_node = self.create_selector_node(name)
        elif type_ == "sequence":
            composite_node = self.create_sequence_node(name)
        elif type_ == "parallel":
            composite_node = self.create_parallel_node(name)
        elif type_ == "repeater":
            composite_node = self.create_repeater_node(name)
        elif type_ == "parsel":
            composite_node = self.create_par_sel_node(name)
        return composite_node

    def create_selector_node(self, name):
        if "Selector" not in name:
            if "selector" in name:
                name = name.replace("selector", "Selector")
            else:
                name = "Selector_" + name
            name = "Selector" #hardcoded for analysis
        return pt.composites.Selector(name=name)

    def create_sequence_node(self, name):
        if "Sequence" not in name:
            if "sequence" in name:
                name = name.replace("sequence", "Sequence")
            else:
                name = "Sequence_" + name
            name = "Sequence" #hardcoded for analysis
        return pt.composites.Sequence(name=name)


    def create_parallel_node(self, name):
        if "||" not in name:
            name = "||_" + name
        name = "||" #hardcoded for analysis
        return pt.composites.Parallel(name=name)

    def create_repeater_node(self, name):
        return pt.composites.Sequence(name="Repeat<>")

    def create_par_sel_node(self, name):
        return pt.composites.Parallel(name="|| / Selector")
