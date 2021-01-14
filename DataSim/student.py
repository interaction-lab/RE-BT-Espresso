import py_trees as pt
import random
from globals import student_vars, env_vars

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