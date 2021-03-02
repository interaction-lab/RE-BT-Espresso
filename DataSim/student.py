import py_trees as pt
import random
from globals import student_vars, env_vars

class Student():
    def __init__(self):
        self.setup()
        
    def setup(self):
        self.blackboard = pt.blackboard.Client(name="Student")
        self.init_read_write_access()
        self.reset_state()
        
    def init_read_write_access(self):
        for key in student_vars:
            self.blackboard.register_key(key=key, access=pt.common.Access.WRITE)
        for key in env_vars:
            self.blackboard.register_key(key=key, access=pt.common.Access.READ)

    def reset_state(self):
        for key in student_vars:
            self.blackboard.set(key, 0, True)

    def update(self):
        #update random state variable
        key = random.randint(0, len(student_vars)-1)
        state_var = student_vars[key]
        new_value = random.random()
        self.blackboard.set(state_var, new_value, True)