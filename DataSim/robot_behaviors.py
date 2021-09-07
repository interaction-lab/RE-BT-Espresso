from os import stat
from bt_sim import pt
import random
import globals as g

# extend py_trees w/ Repeater
import itertools
import typing
from py_trees import common


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
        
write_this_turn = True
class Action(pt.behaviour.Behaviour):
    def __init__(self, name, p_correct):
        super().__init__(name=name)
        self.p_correct = p_correct
        if "action" not in self.name:
            self.name = "action_" + self.name # needed for results
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key="success", access=pt.common.Access.WRITE)
        self.blackboard.register_key(key="robot_action", access=pt.common.Access.WRITE)
            
    def update(self):
        global write_this_turn

        status = self.do_act() if random.random() <= self.p_correct else self.fail_act()
        write_this_turn = random.random() > 0.4
        if write_this_turn:
            g.csv_writer.writerow(pt.blackboard.Blackboard.storage) # how to deal with repeaters....
            return status
        return pt.common.Status.RUNNING

    def do_act(self):
        self.blackboard.robot_action = self.name
        self.blackboard.success = True
        return pt.common.Status.SUCCESS
    
    def fail_act(self):
        self.blackboard.success = False
        return pt.common.Status.FAILURE
    
class Repeater(pt.composites.Sequence):
    def __init__(self, 
        num_repeats,
        name: str="Repeat<>",
        memory: bool=True,
        children: typing.List[pt.behaviour.Behaviour]=None,
        ):

        super().__init__(name=name, memory=memory, children=children)
        self.num_repeats = num_repeats
        self.at_iter = 0

    def tick(self):
        """
        Tick over the children.

        Yields:
            :class:`~py_trees.behaviour.Behaviour`: a reference to itself or one of its children
        """
        self.logger.debug("%s.tick()" % self.__class__.__name__)

        # initialise
        index = 0
        if self.status != common.Status.RUNNING or not self.memory:
            self.current_child = self.children[0] if self.children else None
            for child in self.children:
                if child.status != common.Status.INVALID:
                    child.stop(common.Status.INVALID)
            # user specific initialisation
            self.initialise()
            self.at_iter = 0 # reset repeater
        else:  # self.memory is True and status is RUNNING
            index = self.children.index(self.current_child)

        # customised work
        self.update()

        # nothing to do
        if not self.children:
            self.current_child = None
            self.stop(common.Status.SUCCESS)
            yield self
            return

        # actual work
        while self.at_iter < self.num_repeats:
            for child in itertools.islice(self.children, index, None):
                for node in child.tick():
                    yield node
                    if node is child and node.status != common.Status.SUCCESS:
                        self.status = node.status
                        yield self
                        return
                try:
                    # advance if there is 'next' sibling
                    self.current_child = self.children[index + 1]
                    index += 1
                except IndexError:
                    pass
            self.at_iter += 1
            index = 0

        self.stop(common.Status.SUCCESS)
        yield self

