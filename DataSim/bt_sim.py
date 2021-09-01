import py_trees as pt
import csv
import json
import globals as g
from world import World
from student import Student
from tree_units import*
import os

def run_sim(path):
    print("Start Sim")
    pt.logging.level = pt.logging.Level.WARN
    pt.blackboard.Blackboard.enable_activity_stream(100)
    
    g.remove_folder_if_exists(path)
    os.makedirs(path)

    with open(sys.argv[1]) as rc:
        r = Tree_Basic(**json.loads(rc.read()))
        r.render_tree()

    s = Student()
    w = World()

    with open(g.global_output_folder + g.config_folder_name + g.output_filename, mode='w') as csv_file:
        g.csv_writer = csv.DictWriter(csv_file,\
            fieldnames=pt.blackboard.Blackboard.keys())
        g.csv_writer.writeheader()

        for t in range(g.num_rows):
            g.csv_writer.writerow(pt.blackboard.Blackboard.storage)
            s.update()
            w.update()
            r.b_tree.tick()
    print("done")

def main():
    g.config_folder_name = sys.argv[1].replace(".json", "") + "/"
    path = os.getcwd() + "/" + g.global_output_folder + g.config_folder_name
    run_sim()
        
if __name__ == '__main__':
    main()