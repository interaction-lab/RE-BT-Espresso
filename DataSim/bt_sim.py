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
          
    with open(sys.argv[1]) as rc:
        r = Tree_Basic(**json.loads(rc.read()))
        r.render_tree()

    s = Student()
    w = World()

    with open(g.output_filename, mode='w') as csv_file:
        g.csv_writer = csv.DictWriter(csv_file,\
            fieldnames=pt.blackboard.Blackboard.keys())
        g.csv_writer.writeheader()

        for t in range(25):
            g.csv_writer.writerow(pt.blackboard.Blackboard.storage)
            s.update()
            w.update()
            r.b_tree.tick()
            print(w.blackboard)

    print("done")
        
if __name__ == '__main__':
    main()