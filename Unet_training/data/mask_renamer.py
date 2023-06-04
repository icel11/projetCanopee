import os

directory = "."  # Set the directory path where the files are located

for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)):
        base_name, extension = os.path.splitext(filename)
        new_filename = "mask_" + base_name + extension
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))