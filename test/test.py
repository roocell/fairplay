# this will run the fairplay.py script supplying all the test data
# any assert is a failure

# this directory contains a series of test (one in each folder with input files) to test the algorithm
# verification is built into the script - and will assert if there's an error.

# loop through subfolders in this directory
import os
import sys

# Add the parent directory to the sys.path
parent_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_directory)

from logger import log as log
import fairplay

# TODO: accept argument to run one test

# Get the current directory
current_directory = os.getcwd()

# Iterate through subfolders in the current directory
for subfolder in os.listdir(current_directory):
  if os.path.isdir(subfolder):
    subfolder_path = os.path.join(current_directory, subfolder)
    players_file = os.path.join(subfolder_path, "players.txt")
    stronglines_file = os.path.join(subfolder_path, "stronglines.txt")
    prevshifts_file = os.path.join(subfolder_path, "prevshifts.txt")

    # Check if the required files exist in the subfolder
    if os.path.exists(players_file) and os.path.exists(
        stronglines_file) and os.path.exists(prevshifts_file):
      # Call fairplay.py with the specified arguments
      log.debug(f"<<<<<<<< running {subfolder_path} >>>>>>>>>>>>>>>")
      fairplay.run_fairplay_algo(players_file, stronglines_file,
                                 prevshifts_file)
      log.debug(f"<<<<<<<< done {subfolder_path} >>>>>>>>>>>>>>>")

    else:
      print(f"Skipping '{subfolder}' - Missing one or more required files.")
