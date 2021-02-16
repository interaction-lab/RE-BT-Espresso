import py_trees as pt
import csv
import json
import globals as g
from world import World
from student import Student
from tree_units import*


def main():
    print("start")
    pt.logging.level = pt.logging.Level.DEBUG
    pt.blackboard.Blackboard.enable_activity_stream(100)
    
    with open(g.student_cfg_path) as sc:
        s = Student(**json.loads(sc.read()))
        
    with open(g.robot_cfg_path) as rc:
        r = Tree_Basic(**json.loads(rc.read()))
        r.render_tree()
        
    with open(g.world_cfg_path) as wc:
        #w = World(**json.loads(wc.read()))
        w = World()

    with open(g.output_filename, mode='w') as csv_file:
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