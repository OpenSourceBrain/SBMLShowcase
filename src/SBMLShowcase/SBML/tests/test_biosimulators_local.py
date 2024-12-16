#!/usr/bin/env python

"""
This script tests the compatibility of different biosimulation engines with a given SBML and SED-ML file.
It runs each engine and saves a JSON file with the log.yml file (as a dict), and the d1 plot for each engine.
"""

import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)  # to import utils
import argparse
import json

import utils

# Save the current working directory
cwd = os.getcwd()
print("Current working directory:", cwd)

# SBML folder is one folder up relative to cwd
path_to_sbml_folder = os.path.abspath(os.path.join(cwd, os.pardir))
print("Path to SBML folder:", path_to_sbml_folder)

# change the working directory to the SBML folder (because here the SBML and SED-ML files are located)
os.chdir(path_to_sbml_folder)
print("Changed working directory to:", os.getcwd())

sbml_file_name = "LEMS_NML2_Ex9_FN.sbml"
sedml_file_name = "LEMS_NML2_Ex9_FN_missing_xmlns.sedml"  # xmlns:sbml missing

# output_dir is set to 'd1_plots' by default but can be changed using the --output-dir argument (required to deal with GitHub Actions permission issues)
parser = argparse.ArgumentParser(
    description="Test compatibility of different biosimulation engines"
)
parser.add_argument(
    "--output-dir",
    action="store",
    default="d1_plots",
    help="prefix of the output directory where the d1 plots will be saved",
)
args = parser.parse_args()

test_folder = "tests"

d1_plots_local_dir = os.path.join(test_folder, args.output_dir + "_local")

print("d1 plots will be saved in:", d1_plots_local_dir)

engine_keys = list(utils.ENGINES.keys())

results_local = utils.run_biosimulators_locally(
    engine_keys,
    sedml_file_name=sedml_file_name,
    sbml_file_name=sbml_file_name,
    d1_plots_local_dir=d1_plots_local_dir,
    test_folder=test_folder,
)

results_local_path = os.path.join(path_to_sbml_folder, "tests", "results_local.json")
with open(results_local_path, "w") as fp:
    json.dump(results_local, fp, indent=4)
