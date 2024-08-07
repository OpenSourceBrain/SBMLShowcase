#!/usr/bin/env python

'''
This script tests the compatibility of different biosimulation engines with a given SBML and SED-ML file.
It runs each engine and records the result (pass/fail) and any error messages encountered during the simulation.
The results are then displayed in a table and saved to a markdown file.
'''

import sys
sys.path.append("..")
import utils
import os
import pandas as pd
import shutil
import yaml
import argparse

parser = argparse.ArgumentParser(description='Test compatibility of different biosimulation engines')
parser.add_argument('--output-dir',action='store',default='d1_plots',help='prefix of the output directory where the d1 plots will be saved')
args = parser.parse_args()

d1_plots_remote_dir = args.output_dir + '_remote'
d1_plots_local_dir = args.output_dir + '_local'

sbml_filepath = 'LEMS_NML2_Ex9_FN.sbml'
sedml_filepath = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing

engines = utils.engines
types_dict = utils.types_dict


#########################################################################################
# Run remotely
#########################################################################################

remote_output_dir = 'remote_results'

download_links_dict = dict()
for e in engines.keys():
    download_link = utils.run_biosimulators_remote(e, sedml_filepath, sbml_filepath)
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

output_folder = 'output'

for e in engines.keys():
    print('Running ' + e)
    output_dir = os.path.abspath(os.path.join(output_folder, e))
    record = utils.run_biosimulators_docker(e, sedml_filepath, sbml_filepath, output_dir=output_dir)
    results_local[e] = record

file_paths = utils.find_files(output_folder, '.pdf')
utils.move_d1_files(file_paths, d1_plots_local_dir)

# if it exists remove the output folder
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
    print('Removed ' + output_folder + ' folder')

#########################################################################################
# process results and save markdown table
#########################################################################################

results_table = utils.create_results_table(results, types_dict, sbml_filepath, sedml_filepath, engines, d1_plots_remote_dir
results_table_local = utils.create_results_table(results_local, types_dict, sbml_filepath, sedml_filepath, engines, d1_plots_local_dir)

# rename cols to distinguish between local and remote results except for Engine column
results_table.columns = [str(col) + ' (remote)' if col != 'Engine' else str(col) for col in results_table.columns]
results_table_local.columns = [str(col) + ' (local)' if col != 'Engine' else str(col) for col in results_table_local.columns]

# combine remote and local results
combined_results = pd.merge(results_table, results_table_local, on='Engine', how='outer')
combined_results = combined_results.reindex(columns=['Engine'] + sorted(combined_results.columns[1:]))

cols_order = ['Engine', 'pass/FAIL (remote)', 'pass/FAIL (local)',\
               'Compatibility (remote)', 'Compatibility (local)', \
               'Type (remote)', \
               'Error (remote)', 'Error (local)', \
               'd1 (remote)', 'd1 (local)']

combined_results = combined_results[cols_order]

# save the results to a markdown file
with open('results_compatibility_biosimulators.md', 'w') as f:
    f.write(combined_results.to_markdown())
