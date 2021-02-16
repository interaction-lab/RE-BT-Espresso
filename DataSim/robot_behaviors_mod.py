import py_trees as pt
import random

'''Sense parent class'''
class Condition(pt.behaviour.Behaviour):
    def __init__(self, name, p_correct):
        self.p_correct = p_correct
        super().__init__(name="")
            
    def update(self):
        if random.random() <= self.p_correct:
            return self.check()
        else:
            return not self.check()
    
    def check(self):
        pass
    
'''Sense child classes'''
class Check_State(Condition):
    def __init__(self, n, p):
        super().__init__(name=n, p_correct=p)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_action", access=pt.common.Access.READ)

    def check(self):
        if self.blackboard.get(self.name) < 0.5:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE


'''Action parent class'''
class Act(pt.behaviour.Behaviour):
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
