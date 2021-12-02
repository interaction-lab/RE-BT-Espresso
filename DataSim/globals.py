import os
import shutil

student_cfg_path = 'configs/student_config.json'
robot_cfg_path = 'configs/robot_config.json'
world_cfg_path = 'configs/world_config.json'
output_filename = "simulated_data.csv"
global_output_folder = "sim_data/"
config_folder_name = ""

num_rows = 20000

csv_writer = None

env_vars = [
    "Time",
    "env_state_var_1",
    "env_state_var_2",
    "env_state_var_3",
    "env_state_var_4",
    "env_state_var_5",
    "env_state_var_6"
]

student_vars = [
    "stu_state_var_1",
    "stu_state_var_2",
    "stu_state_var_3",
    "stu_state_var_4",
    "stu_state_var_5",
    "stu_state_var_6"
]

robot_vars = [
    "robot_action",
    "success"
]


def combine_folder_and_working_dir(folder_name, working_directory):
    if working_directory:
        return os.fsdecode(os.path.join(working_directory, folder_name))
    return folder_name


def does_folder_exist_in_directory(folder_name, working_directory=None):
    potential_directory = combine_folder_and_working_dir(
        folder_name, working_directory)
    return os.path.isdir(potential_directory), potential_directory


def remove_folder_if_exists(folder_name, working_directory=None):
    dir_exists, dir_path = does_folder_exist_in_directory(
        folder_name, working_directory)
    if dir_exists:
        print(f"Removing prior directory {dir_path}")
        shutil.rmtree(dir_path)
