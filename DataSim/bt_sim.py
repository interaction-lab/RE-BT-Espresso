import py_trees as pt
import csv
import random
import copy
from robot import Robot
from world import World
from student import Student

filename = "simulated_data.csv"

def main():
    print("start")
    pt.logging.level = pt.logging.Level.DEBUG
    pt.blackboard.Blackboard.enable_activity_stream(100)

    w = World()
    r = Robot()
    s = Student()

    with open(filename, mode='w') as csv_file:
        csv_writer = csv.DictWriter(csv_file,\
            fieldnames=pt.blackboard.Blackboard.keys())
        csv_writer.writeheader()

        for t in range(25):
            csv_writer.writerow(pt.blackboard.Blackboard.storage)
            s.update()
            w.update()
            r.b_tree.tick()
            print(w.blackboard)

    print("done")
        
if __name__ == '__main__':
    main()