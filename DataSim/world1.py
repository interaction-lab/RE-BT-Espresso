import py_trees as pt
import random

from py_trees import blackboard
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
        for key in student_vars:
            self.blackboard.register_key(key=key, access=pt.common.Access.READ)

    def reset_world_state(self):
        for key in env_vars:
            self.blackboard.set(key, 0, True)

    def update(self):
        #update random state variable
        key = random.randint(1, len(env_vars)-1)
        state_var = env_vars[key]
        new_value = random.random()
        self.blackboard.set(state_var, new_value, True)

        self.update_time()

    def check_student_state(self):
        return self.blackboard.Submit

    def update_time(self):
        self.blackboard.Time += 1