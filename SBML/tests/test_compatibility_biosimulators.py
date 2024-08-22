#!/usr/bin/env python

"""
This script tests the compatibility of different biosimulation engines with a given SBML and SED-ML file.
It runs each engine and records the result (pass/fail) and any error messages encountered during the simulation.
The results are then displayed in a table and saved to a markdown file.
"""

import sys
import os

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import utils
import os
import pandas as pd
import shutil
import yaml
import argparse

# Save the current working directory
cwd = os.getcwd()
print('Current working directory:', cwd)

# SBML folder is one folder up relative to cwd
path_to_sbml_folder = os.path.abspath(os.path.join(cwd, os.pardir))
print('Path to SBML folder:', path_to_sbml_folder)

# change the working directory to the SBML folder
os.chdir(path_to_sbml_folder)
print('Changed working directory to:', os.getcwd())

sbml_file_name = 'LEMS_NML2_Ex9_FN.sbml'
sedml_file_name = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing

sbml_file_path = os.path.join(path_to_sbml_folder, sbml_file_name)
sedml_file_path = os.path.join(path_to_sbml_folder, sedml_file_name)

engines = utils.engines
types_dict = utils.types_dict

print('Path to SED-ML file:', sedml_file_path)
print('Path to SBML file:', sbml_file_path)

parser = argparse.ArgumentParser(description='Test compatibility of different biosimulation engines')
parser.add_argument('--output-dir',action='store',default='d1_plots',help='prefix of the output directory where the d1 plots will be saved')
args = parser.parse_args()

test_folder = 'tests'

d1_plots_remote_dir = os.path.join(test_folder, args.output_dir + '_remote')
d1_plots_local_dir = os.path.join(test_folder, args.output_dir + '_local')

print('d1 plots will be saved in:', d1_plots_remote_dir, 'and', d1_plots_local_dir)

#########################################################################################
# Run remotely
#########################################################################################

remote_output_dir = 'remote_results'
remote_output_dir = os.path.join(test_folder, remote_output_dir)

download_links_dict = dict()
for e in engines.keys():
    download_link = utils.run_biosimulators_remote(e, sedml_file_name, sbml_file_name)
    download_links_dict[e] = download_link

extract_dir_dict = dict()
for e, link in download_links_dict.items():
    extract_dir = utils.get_remote_results(e, link, remote_output_dir)
    extract_dir_dict[e] = extract_dir

results = dict()
for e, extract_dir in extract_dir_dict.items():
    status = ""
    error_message = ""
    exception_type = ""

    log_yml_path = utils.find_file_in_dir('log.yml', extract_dir)[0]
    if not log_yml_path:
        status = None
        error_message = 'log.yml not found'
        continue
    with open(log_yml_path) as f:
        log_yml_dict = yaml.safe_load(f)
        if log_yml_dict['status'] == 'SUCCEEDED':
            status = 'pass'
        elif log_yml_dict['status'] == 'FAILED':
            status = 'FAIL'
            exception = log_yml_dict['exception']
            error_message = exception['message']
            exception_type = exception['type'] 
        else:
            status = None
        results[e] = [status, error_message, exception_type] 

file_paths = utils.find_files(remote_output_dir, '.pdf')
utils.move_d1_files(file_paths, d1_plots_remote_dir)

# remove the remote results directory
if os.path.exists(remote_output_dir):
    shutil.rmtree(remote_output_dir)
    print('Removed ' + remote_output_dir + ' folder')

#########################################################################################
# Run locally
#########################################################################################

results_local = {}

output_folder = 'local_results'
local_output_dir = os.path.join(test_folder, output_folder)

for e in engines.keys():
    print('Running ' + e)
    local_output_dir_e = os.path.abspath(os.path.join(local_output_dir, e))
    print(local_output_dir_e)
    record = utils.run_biosimulators_docker(e, sedml_file_name, sbml_file_name, output_dir=local_output_dir_e)
    results_local[e] = record

file_paths = utils.find_files(local_output_dir, '.pdf')
print('file paths:', file_paths)
utils.move_d1_files(file_paths, d1_plots_local_dir)

# if it exists remove the output folder
if os.path.exists(local_output_dir):
    shutil.rmtree(local_output_dir)
    print('Removed ' + local_output_dir + ' folder')

#########################################################################################
# process results and save markdown table
#########################################################################################

results_table = utils.create_results_table(results, types_dict, sbml_file_name, sedml_file_name, engines, d1_plots_remote_dir)
results_table_local = utils.create_results_table(results_local, types_dict, sbml_file_name, sedml_file_name, engines, d1_plots_local_dir)

# rename cols to distinguish between local and remote results except for Engine column
results_table.columns = [str(col) + ' (R)' if col != 'Engine' else str(col) for col in results_table.columns]
results_table_local.columns = [str(col) + ' (L)' if col != 'Engine' else str(col) for col in results_table_local.columns]

# combine remote and local results
combined_results = pd.merge(results_table, results_table_local, on='Engine', how='outer')
combined_results = combined_results.reindex(columns=['Engine'] + sorted(combined_results.columns[1:]))

cols_order = ['Engine', 'pass / FAIL (R)', 'pass / FAIL (L)',\
               'Compat (R)', 'Compat (L)', \
               'Type (R)', \
               'Error (R)', 'Error (L)', \
               'd1 (R)', 'd1 (L)']

combined_results = combined_results[cols_order]

path_to_results = os.path.join(test_folder, 'results_compatibility_biosimulators.md')
print('Saving results to:', path_to_results)
with open(path_to_results, 'w') as f:
    f.write(combined_results.to_markdown())

print('Number of columns in md table:', len(combined_results.columns))
print('Number of rows in md table:', len(combined_results))
print(combined_results.head())
