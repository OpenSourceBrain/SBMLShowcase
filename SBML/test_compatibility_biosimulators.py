#!/usr/bin/env python

import sys
sys.path.append("..")
import utils
import os
import pandas as pd
import shutil

sbml_filepath = 'LEMS_NML2_Ex9_FN.sbml'
sedml_filepath = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing

# Instruction are in different format for these three engines
# OpenCOR:https://docs.biosimulators.org/Biosimulators_OpenCOR/installation.html#python-package-and-command-line-program
# rbapy: https://docs.biosimulators.org/Biosimulators_RBApy/installation.html#command-line-program
# smoldyn: https://smoldyn.readthedocs.io/en/latest/python/api.html#sed-ml-combine-biosimulators-api

engines = ['amici',\
           'brian2',\
           'bionetgen',\
           'boolnet',\
           'cbmpy',\
           'cobrapy',\
           'copasi',\
           'gillespy2',\
           'copasi',\
           'tellurium',\
           'libsbmlsim',\
           'ginsim',\
           'masspy',\
           'opencor',\
           'pysces',\
           'rbapy',\
           'vcell',\
           'xpp',  
           'smoldyn'  

           ]

# to store results
engine_dict = {}

for e in engines:
    print('Running ' + e)
    output_dir = os.path.abspath(os.path.join('output', e))
    try:
        record = utils.run_biosimulators_docker(e, sedml_filepath, sbml_filepath, output_dir=output_dir)
        engine_dict[e] = record
    except Exception as error:
        # get error message
        error_message = str(error)
        print(f"Error occurred while running {e}")
        engine_dict[e] = error_message
        continue

results_table = pd.DataFrame.from_dict(engine_dict, orient='index', columns=['Result'])
results_table.index.name = 'Engine'
results_table.reset_index(inplace=True)
results_table.sort_values('Engine', inplace=True)
results_table['pass/Fail'] = results_table['Result'].apply(lambda x: x[0] if isinstance(x, list) else x)
results_table['Error'] = results_table['Result'].apply(lambda x: x[1] if isinstance(x, list) else None)
results_table['Error'] = results_table['Error'].apply(lambda x: x.replace('```', '') if x else x)
results_table.drop(columns=['Result'], inplace=True)
results_table.to_markdown('results.md', index=False)

# Save the results table to a markdown file
with open('results.md', 'w') as f:
    f.write(results_table.to_markdown(index=False))

# Delete the output folder and its contents
for file_name in os.listdir('output'):
    file_path = os.path.join('output', file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
    elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
