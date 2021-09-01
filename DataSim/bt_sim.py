import py_trees as pt
import csv
import json
import globals as g
from world import World
from student import Student
from tree_units import*
import os

def run_sim(json_file_path_and_name):
    print("Start Sim")
    pt.logging.level = pt.logging.Level.WARN
    pt.blackboard.Blackboard.enable_activity_stream(100)
    json_filename = os.path.basename(json_file_path_and_name)
    output_path = os.getcwd() + "/" + g.global_output_folder + json_filename.replace(".json", "") + "/"
    g.remove_folder_if_exists(output_path)
    os.makedirs(output_path)

    # autofind json 
    with open(json_file_path_and_name) as rc:
        r = Tree_Basic(**json.loads(rc.read()))
        r.render_tree(output_path)

    s = Student()
    w = World()

    with open(output_path + g.output_filename, mode='w') as csv_file:
        g.csv_writer = csv.DictWriter(csv_file,\
            fieldnames=pt.blackboard.Blackboard.keys())
        g.csv_writer.writeheader()

        for t in range(g.num_rows):
            g.csv_writer.writerow(pt.blackboard.Blackboard.storage)
            s.update()
            w.update()
            r.b_tree.tick()
    print(f"Simulation completed for {json_file_path_and_name}")
    return output_path

def main():
    run_sim(sys.argv[1])
        
if __name__ == '__main__':
    main()