import curio
import async_btree as bt
import contextvars
import csv
import random
import copy

world_state = contextvars.ContextVar("world_state", default={"Time":0, "CurExercise": 0, "KC": 0, "SnapTo": None, "ExerciseSubmissionResult": None,\
    "RobotPhysicalAction": None, "RobotDialogue": None, "SimComplete": False})
time_step = contextvars.ContextVar("time_step", default=0.02)
interaction_length = contextvars.ContextVar("interaction_length", default=10)
filename = contextvars.ContextVar("filename", default="simulated_data.csv")
sleep_time_scale = contextvars.ContextVar("sleep_time_scale", default=100)

NOISE_LVL = 0.5 #0 to 1, robot reactions occur perfectly when NOISE_LVL=1
KC_UPPER_BOUND = 10 #for generating KC values

#probability submitted exercise is correct
def try_submit_exercise():
    p_correct = world_state.get()["KC"]/KC_UPPER_BOUND
    return p_correct

#probability person chooses to submit the exercise
def choose_submit_exercise():
    p_choose = random.random()
    return p_choose

#probability person chooses to snap something
def choose_snap_action():
    p_choose = random.random()
    return p_choose

async def main():
    print("start")
    m = Master()
    r = Robot(m)
    h = Human(m)
    d = DataSimulator()
    async with curio.TaskGroup(wait=all) as g:
        await g.spawn(d.run_simulation)
        await g.spawn(r.listen)
        await g.spawn(h.b_tree)
    print(world_state.get())
    print("done")


def clear_world_state():
    world_state.get()["RobotAction"] = ""
    world_state.get()["KC"] = ""

class Master():
    def __init__(self):
        self.msg = dict([("result", None), ("action", None)])

    def push_message(self, action, result):
        self.msg["action"] = action
        self.msg["result"] = result

    def pull_message(self):
        temp = copy.deepcopy(self.msg)
        self.msg["action"] = None
        self.msg["result"] = None
        return temp

class Human():    
    def __init__(self, master):
        self.define_tree()
        self.master = master

    async def decide_submit_answer(self):
        p_choose_submit_answer = choose_submit_exercise()
        result = random.random() < p_choose_submit_answer
        await curio.sleep(1/sleep_time_scale.get())
        return result
    
    async def decide_snap_action(self):
        p_choose_snap_action = choose_snap_action()
        result = random.random() < p_choose_snap_action
        await curio.sleep(1/sleep_time_scale.get())
        return result

    async def submit_answer(self):
        p_correct = try_submit_exercise()
        result = random.random() < p_correct
        world_state.get()["ExerciseSubmissionResult"] = result  #True=correct
        await curio.sleep(1/sleep_time_scale.get())
        world_state.get()["ExerciseSubmissionResult"] = None
        self.master.push_message("submit", result)
        if(result):
            self.next_exercise()
        return result

    async def snap_action(self):
        world_state.get()["SnapTo"] = "snap something"
        await curio.sleep(1/sleep_time_scale.get())
        world_state.get()["SnapTo"] = None
        return True
        
    def next_exercise(self):
        world_state.get()["CurExercise"] += 1
        return True
    
    def define_tree(self):

        #snapping blocks
        self.a_decide_snap_action = bt.action(target=self.decide_snap_action)
        self.a_snap_action = bt.action(target=self.snap_action)
        self.sq_snap_action = bt.sequence(children=[
            self.a_decide_snap_action,
            self.a_snap_action
        ])
        self.sc_snap_action = bt.always_success(child=self.sq_snap_action)

        #exercise submissions
        self.a_decide_submit_answer = bt.action(target=self.decide_submit_answer)
        self.a_submit_answer = bt.action(target=self.submit_answer)

        #exercise 1, TODO: make exercise less generic
        self.sq_exercise_1 = bt.sequence(children = [
            self.sc_snap_action,
            self.a_decide_submit_answer,
            self.a_submit_answer,
        ])
        self.r_exercise_1 = bt.retry_until_success(child=self.sq_exercise_1)

        #exercise 2
        self.sq_exercise_2 = bt.sequence(children = [
            self.sc_snap_action,
            self.a_decide_submit_answer,
            self.a_submit_answer,
        ])
        self.r_exercise_2 = bt.retry_until_success(child=self.sq_exercise_2)

        #all exercises
        self.sq_all_exercises = bt.sequence(children = [
            #TODO: add more exercises? temp placeholders
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1,
            self.r_exercise_1
        ])

        self.b_tree = self.sq_all_exercises
        print(bt.stringify_analyze(bt.analyze(self.b_tree)))

class Robot():
    def __init__(self, master):
        self.master = master

    #probability that the robot will react
    def react_success(self): 
        p_success = max(NOISE_LVL, random.random())
        return p_success

    async def listen(self):
        while(world_state.get()["SimComplete"]==False):
            msg = self.master.pull_message()
            self.react(msg)
            await curio.sleep(0.01/sleep_time_scale.get())
        return None

    def react(self, msg):
        if(msg["action"]!=None):
            action_success = random.random() < self.react_success()
            dialogue_success = random.random() < self.react_success()
            if(action_success):
                if(msg["result"]==True):
                    self.do_pos_action()
                else:
                    self.do_neg_action()
            if(dialogue_success):
                if(msg["result"]==True):
                    self.do_pos_dialogue()
                else:
                    self.do_neg_dialogue()
        else:
            world_state.get()["RobotPhysicalAction"] = None
            world_state.get()["RobotDialogue"] = None

    def do_pos_action(self):
        world_state.get()["RobotPhysicalAction"] = "Action1"

    def do_pos_dialogue(self):
        world_state.get()["RobotDialogue"] = "Dialogue1"

    def do_neg_action(self):
        world_state.get()["RobotPhysicalAction"] = "Action2"

    def do_neg_dialogue(self):
        world_state.get()["RobotDialogue"] = "Dialogue2"


class DataSimulator:
    def __init__(self):
       self.reset_simulation()

    def reset_simulation(self):
        world_state.get()["Time"] = 0

    def update_time(self):
        world_state.get()["Time"] += time_step.get()

    def interaction_is_running(self):
        return world_state.get()["Time"] < interaction_length.get()
            
    async def update_state(self):
        self.update_time()
        world_state.get()["KC"] = random.randint(0, KC_UPPER_BOUND) #random KC
        await curio.sleep(time_step.get()/sleep_time_scale.get())
    
    async def run_simulation(self):
        print("Running sim")
        world_state.get()["SimComplete"] = False
        with open(filename.get(), mode='w') as csv_file:
            csv_writer = csv.DictWriter(csv_file,\
                fieldnames=world_state.get().keys())
            csv_writer.writeheader()
            while self.interaction_is_running():
                csv_writer.writerow(world_state.get())
                await self.update_state()
                #clear_world_state()
        world_state.get()["SimComplete"] = True
        return None
        
if __name__ == '__main__':
    curio.run(main, with_monitor=False)
   