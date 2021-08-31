"""Generally runs DTree -> behavior tree, in need of change per #19

Creates decision trees, checks measures, prunes, and converts them to behavior  trees using behaviorTree_Builder

Attributes:
    PRUNING_GRAPH_FILENAME (str): filepath constant for acurracy vs alpha output graph
"""

import graphviz
import pipeline_constants as constants
import pydot
import re
import argparse
import glob
import os
import pathlib

def process_command_line_args():
	"""
	Returns:
	    tuple(str, str): Command line args for (config, output) files
	
	"""
	ap = argparse.ArgumentParser()
	ap.add_argument("-d", "--directory", required = True, help = "Path to dot file directory")
	args = vars(ap.parse_args())
	return args["directory"]


def main():
	"""Colors behavior tree files
	"""
	directory = process_command_line_args()
	# should all be from constants
	output_filename = "output~"

	lat_seq_name = constants.LAT_SEQ_NAME + "*"
	lat_fillcolor = "#39FF14"

	par_replace_sel_name = constants.SEL_PAR_REPLACEABLE_NAME + "*"
	par_replace_sel_fillcolor = "#FF1818"

	action_replace_name = constants.ACTION_NODE_STR + "*"
	action_replace_fillcolor = "#FFC0CB"

	repeat_replace_name = constants.REPEAT_SEQ_NAME + "*"
	repeat_replace_fillcolor = "#C3B1E1"

	for full_filepath in pathlib.Path(directory).glob("**/*.dot"):
		filename = full_filepath.name
		files_dir = str(full_filepath).replace(filename, "")
		if output_filename in filename:
			continue # stop inf recur
		print("Re-coloring: " + str(full_filepath))
		graph = pydot.graph_from_dot_file(full_filepath)[0]
		nodes = graph.get_nodes()
		# if only there were data structures that would make this loopable... lol
		for node in nodes:
			if re.search(lat_seq_name, node.get_name()):
				node.set_fillcolor(lat_fillcolor)
			elif re.search(par_replace_sel_name, node.get_name()):
				node.set_fillcolor(par_replace_sel_fillcolor)
			elif re.search(action_replace_name, node.get_name()):
				node.set_fillcolor(action_replace_fillcolor)
			elif re.search(repeat_replace_name, node.get_name()):
				node.set_fillcolor(repeat_replace_fillcolor) 
		
		output_directory = files_dir + "/" + filename + "re_colored/"
		if not os.path.exists(output_directory):
			os.mkdir(output_directory)

		full_output_name = output_directory + output_filename
		graph.write_svg(full_output_name + ".svg")
		graph.write_dot(full_output_name + ".dot")
		graph.write_png(full_output_name + ".png")

if __name__ == '__main__':
	main()
