#!/usr/bin/env python3

"""
produce a markdown table of the results of running various tests on the SBML Test Suite

get this version of the test suite that includes sedml versions or the sedml validation will fail:
https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip
"""

import os
import sys
import json
sys.path.append("..")
import utils
engines = utils.ENGINES


def create_test_suite_results_tables():
    """
    Create a table of results for each test case in the test suite

    """
    starting_dir = os.getcwd() 
    print('Current working directory:', starting_dir)
    subfolders = [f for f in os.listdir(starting_dir) if os.path.isdir(f) and f.startswith('test_')]

    print(subfolders)

    for subfolder in subfolders:
        subfolder_path = os.path.join(starting_dir, subfolder)
        os.chdir(subfolder_path)
        print(f"Changed to {os.getcwd()}")

        test_folder = 'tests'

        results_paths = {
            "local": os.path.join(subfolder_path, test_folder, 'results_local.json'),
            "remote": os.path.join(subfolder_path, test_folder, 'results_remote.json')
        }

        results = {}
        for key, path in results_paths.items():
            with open(path, 'r') as f:
                results[key] = json.load(f)

        d1_plot_paths = {
            "local": os.path.join(subfolder_path, test_folder, 'd1_plots_local'),
            "remote": os.path.join(subfolder_path, test_folder, 'd1_plots_remote')
        }

        # get sbml filename with reg ex (it should contain sbml but not sedml)
        sbml_file_name = [f for f in os.listdir(subfolder_path) if 'sbml' in f and 'sedml' not in f][0]
        # also sbml file does not end with omex
        sbml_file_name = [f for f in os.listdir(subfolder_path) if 'sbml' in f and 'sedml' not in f and not f.endswith('omex')][0]
        sedml_file_name = [f for f in os.listdir(subfolder_path) if 'sedml' in f and not f.endswith('omex')][0]

        results_table = utils.create_combined_results_table(results["remote"], 
                                        results["local"], 
                                        sedml_file_name, 
                                        sbml_file_name, 
                                        d1_plot_paths["local"], 
                                        d1_plot_paths["remote"],
                                        test_folder='tests')
        
        
        print(results_table)


if __name__ == "__main__":
    create_test_suite_results_tables()
