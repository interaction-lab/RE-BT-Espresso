from os import stat
from bt_sim import pt
import random
import globals as g

class Condition(pt.behaviour.Behaviour):
    def __init__(self, name, p_correct, target_state, threshold):
        super().__init__(name=name)
        self.p_correct = p_correct
        self.target_state = target_state
        self.threshold = threshold
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="robot_action", access=pt.common.Access.WRITE)
        self.blackboard.register_key(key=target_state, access=pt.common.Access.READ)
            
    def update(self):
        if random.random() <= self.p_correct:
            status = self.check()
            return status
        else:
            status = self.fail_check()
            return status
    
    def check(self):
        if self.blackboard.get(self.target_state) < self.threshold:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE
        
    def fail_check(self):
        if self.blackboard.get(self.target_state) < self.threshold:
            return pt.common.Status.FAILURE
        else:
            return pt.common.Status.SUCCESS
        

class Action(pt.behaviour.Behaviour):
    def __init__(self, name, p_correct):
        super().__init__(name="A->" + name)
        self.p_correct = p_correct
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="success", access=pt.common.Access.WRITE)
        self.blackboard.register_key(key="robot_action", access=pt.common.Access.WRITE)
            
    def update(self):
        if random.random() <= self.p_correct:
            status = self.do_act()
            g.csv_writer.writerow(pt.blackboard.Blackboard.storage)
            return status
        else:
            status = self.fail_act()
            g.csv_writer.writerow(pt.blackboard.Blackboard.storage)
            return status
    
    def do_act(self):
        self.blackboard.robot_action = self.name
        self.blackboard.success = True
        return pt.common.Status.SUCCESS
    
    def fail_act(self):
        self.blackboard.success = False
        return pt.common.Status.FAILURE
    

