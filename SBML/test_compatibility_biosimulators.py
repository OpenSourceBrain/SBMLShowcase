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

sbml_filepath = 'LEMS_NML2_Ex9_FN.sbml'
sedml_filepath = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing (original file)


engines = utils.engines
types_dict = utils.types_dict

engine_dict = {}

for e in engines.keys():
    print('Running ' + e)
    output_dir = os.path.abspath(os.path.join('output', e))
    try:
        record = utils.run_biosimulators_docker(e, sedml_filepath, sbml_filepath, output_dir=output_dir)
        engine_dict[e] = record
    except Exception as error:
        error_message = str(error)
        print(f"Error occurred while running {e}")
        engine_dict[e] = error_message
        continue

utils.delete_output_folder('output')

# Create a table of the results
results_table = pd.DataFrame.from_dict(engine_dict).T
results_table.columns = ['pass/FAIL', 'Error']
results_table.index.name = 'Engine'
results_table.reset_index(inplace=True)

results_table['Error'] = results_table.apply(lambda x: None if x['pass/FAIL'] == x['Error'] else x['Error'], axis=1)
results_table['pass/FAIL'] = results_table['pass/FAIL'].replace('other', 'FAIL')

results_table['Error'] = results_table['Error'].apply(lambda x: utils.parse_error_message(x))
results_table['Error'] = results_table['Error'].apply(lambda x: utils.collapsible_content(x))

results_table['Compatibility'] = results_table['Engine'].apply(lambda x: utils.check_file_compatibility_test(x, types_dict, sbml_filepath, sedml_filepath))
results_table['Compatibility'] = results_table['Compatibility'].apply(lambda x: utils.collapsible_content(x[1], title=x[0]))
results_table['pass/FAIL'] = results_table['pass/FAIL'].apply(lambda x: f'<span style="color:darkred;">{x}</span>' if x == 'FAIL' else x)
results_table['Compatibility'] = results_table['Compatibility'].apply(lambda x: f'<span style="color:darkred;">{x}</span>' if 'FAIL' in x else x)

results_table = results_table.to_markdown(index=False)

# save results_md_table
with open('results_biosimulators_compatability.md', 'w', encoding='utf-8') as f:
    f.write(results_table)

# #!/usr/bin/env python

# import sys
# sys.path.append("..")
# import utils
# import os
# import pandas as pd
# import shutil

# sbml_filepath = 'LEMS_NML2_Ex9_FN.sbml'
# sedml_filepath = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing

# # Instruction are in different format for these three engines
# # OpenCOR:https://docs.biosimulators.org/Biosimulators_OpenCOR/installation.html#python-package-and-command-line-program
# # rbapy: https://docs.biosimulators.org/Biosimulators_RBApy/installation.html#command-line-program
# # smoldyn: https://smoldyn.readthedocs.io/en/latest/python/api.html#sed-ml-combine-biosimulators-api

# engines = ['amici',\
#            'brian2',\
#            'bionetgen',\
#            'boolnet',\
#            'cbmpy',\
#            'cobrapy',\
#            'copasi',\
#            'gillespy2',\
#            'copasi',\
#            'tellurium',\
#            'libsbmlsim',\
#            'ginsim',\
#            'masspy',\
#            'netpyne',\
#            'neuron',\
#            'opencor',\
#            'pyneuroml',\
#            'pysces',\
#            'rbapy',\
#            'vcell',\
#            'xpp',  
#            'smoldyn'  
#            ]

# engines = {
#                         'amici': ('sbml', 'sedml'),\
#                         'brian2': [('nml', 'sedml'),('lems', 'sedml')],\
#                         'bionetgen': ('bngl', 'sedml'),\
#                         'boolnet': ('sbmlqual', 'sedml'),\
#                         'cbmpy': ('sbml', 'sedml'),\
#                         'cobrapy': ('sbml', 'sedml'),\
#                         'copasi': ('sbml', 'sedml'),\
#                         'gillespy2': ('sbml', 'sedml'),\
#                         'ginsim': ('sbmlqual', 'sedml'),\
#                         'libsbmlsim': ('sbml', 'sedml'),\
#                         'masspy': ('sbml', 'sedml'),\
#                         'netpyne': ('sbml', 'sedml'),\
#                         'neuron': [('nml', 'sedml'),('lems', 'sedml')],\
#                         'opencor': ('sbml', 'sedml'),\
#                         'pyneuroml': [('nml', 'sedml'),('lems', 'sedml')],\
#                         'pysces': ('sbml', 'sedml'),\
#                         'rbapy': ('rbapy', 'sedml'),\
#                         'smoldyn':None ,\
#                         'tellurium': ('sbml', 'sedml'),\
#                         'vcell': None,\
#                         'xpp': ('xpp', 'sedml')               
#                         }


# # to store results
# engine_dict = {}

# for e in engines.keys():
#     print('Running ' + e)
#     output_dir = os.path.abspath(os.path.join('output', e))
#     try:
#         record = utils.run_biosimulators_docker(e, sedml_filepath, sbml_filepath, output_dir=output_dir)
#         engine_dict[e] = record
#     except Exception as error:
#         # get error message
#         error_message = str(error)
#         print(f"Error occurred while running {e}")
#         engine_dict[e] = error_message
#         continue

# results_table = pd.DataFrame.from_dict(engine_dict, orient='index', columns=['Result'])
# results_table.index.name = 'Engine'
# results_table.reset_index(inplace=True)
# results_table.sort_values('Engine', inplace=True)
# results_table['pass/Fail'] = results_table['Result'].apply(lambda x: x[0] if isinstance(x, list) else x)
# results_table['Error'] = results_table['Result'].apply(lambda x: x[1] if isinstance(x, list) else None)
# results_table['Error'] = results_table['Error'].apply(lambda x: x.replace('```', '') if x else x)
# results_table.drop(columns=['Result'], inplace=True)
# results_table.to_markdown('results.md', index=False)

# # Save the results table to a markdown file
# with open('results.md', 'w') as f:
#     f.write(results_table.to_markdown(index=False))

# # Delete the output folder and its contents
# for file_name in os.listdir('output'):
#     file_path = os.path.join('output', file_name)
#     if os.path.isfile(file_path):
#         os.remove(file_path)
#     elif os.path.isdir(file_path):
#         shutil.rmtree(file_path)
