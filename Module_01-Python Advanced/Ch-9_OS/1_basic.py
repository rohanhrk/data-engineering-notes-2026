import os

curr_working_directory = os.getcwd()
print(f"Current Working Directory: {curr_working_directory}")

abs_path = os.path.abspath(__file__)
print(f"Absolute Path of the Current File: {abs_path}")

dir_name = os.path.dirname(abs_path)
print(f"Directory Name of the Current File: {dir_name}")

list_dir = os.listdir(curr_working_directory)
print(f"List of Files and Directories in the Current Directory: {list_dir}")

for i in list_dir:
    if os.path.isfile(i):
        print(f"{i} is a file.")
    elif os.path.isdir(i):
        print(f"{i} is a directory.")

# use case: increamentally load new files from a directory and process them. For example, if you have a directory where new files are added regularly, you can use os.listdir() to get the list of files and then process only the new files that have been added since the last time you checked.

last_load = "2026-11-05"
data_dir = os.path.join(dir_name, "data")
for file_name in os.listdir(data_dir):
    if file_name.split(".")[0] > last_load:
        # process the file here
        print(f"Processing new file: {file_name}")
        