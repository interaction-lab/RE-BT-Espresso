import py_trees as pt
import random

class Condition(pt.behaviour.Behaviour):
    def __init__(self, name, p_correct, target_state):
        super().__init__(name=name)
        self.p_correct = p_correct
        self.target_state = target_state
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_action", access=pt.common.Access.WRITE)
        self.blackboard.register_key(key=target_state, access=pt.common.Access.READ)
            
    def update(self):
        if random.random() <= self.p_correct:
            return self.check()
        else:
            return not self.check()
    
    def check(self):
        if self.blackboard.get(self.target_state) < 0.5:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE

class Action(pt.behaviour.Behaviour):
    def __init__(self, name, p_correct):
        super().__init__(name=name)
        self.p_correct = p_correct
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_action", access=pt.common.Access.WRITE)
            
    def update(self):
        if random.random() <= self.p_correct:
            return self.do_act()
        else:
            return self.fail_act()
    
    def do_act(self):
        self.blackboard.robot_action = self.name
        return pt.common.Status.SUCCESS
    
    def fail_act(self):
        return pt.common.Status.FAILURE
