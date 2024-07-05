'''
This script tests the compatibility of different biosimulation engines with a given SBML and SED-ML file.
It runs each engine and records the result (pass/fail) and any error messages encountered during the simulation.
The results are then displayed in a table and saved to a markdown file.
'''
#!/usr/bin/env python

'''
use pymetadata module to create a minimal valid combine archive
using LEMS_NML2_Ex9_FN.sbml and LEMS_NML2_Ex9_FN.sedml
'''

import sys
sys.path.append("..")
import utils
import os
import pandas as pd
from IPython.display import display_markdown
import shutil
import yaml

sbml_filepath = 'LEMS_NML2_Ex9_FN.sbml'
sedml_filepath = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing

engines = utils.engines
types_dict = utils.types_dict

cwd = os.getcwd()

output_dir = 'remote_results'

download_links_dict = dict()
for e in engines.keys():
    download_link = utils.run_biosimulators_remote(e, sedml_filepath, sbml_filepath)
    download_links_dict[e] = download_link

extract_dir_dict = dict()
for e, link in download_links_dict.items():
    extract_dir = utils.get_remote_results(e, link, output_dir)
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

# make list of pdf files in all directories in values extract_dir_dict
# find all pdf files in cwd/ output_dir
directory = os.path.join(cwd, output_dir)
print(directory)
file_paths = utils.find_files(directory, 'pdf')
utils.move_d1_files(file_paths, 'd1_plots_remote')

# Create a table of the results
results_table = pd.DataFrame.from_dict(results).T
results_table.columns = ['pass/FAIL', 'Error','Type']
results_table.index.name = 'Engine'
results_table.reset_index(inplace=True)

results_table['Error'] = results_table.apply(lambda x: None if x['pass/FAIL'] == x['Error'] else x['Error'], axis=1)
results_table['pass/FAIL'] = results_table['pass/FAIL'].replace('other', 'FAIL')
# results_table['pass/FAIL'] = results_table['pass/FAIL'].apply(lambda x: x if x == 'FAIL' else x)


results_table['Error'] = results_table['Error'].apply(lambda x: utils.ansi_to_html(x))
results_table['Error'] = results_table['Error'].apply(lambda x: utils.collapsible_content(x))

# compatibility_message
results_table['Compatibility'] = results_table['Engine'].apply(lambda x: utils.check_file_compatibility_test(x, types_dict, sbml_filepath, sedml_filepath))
results_table['Compatibility'] = results_table['Compatibility'].apply(lambda x: utils.collapsible_content(x[1], title=x[0]))
results_table['pass/FAIL'] = results_table['pass/FAIL'].apply(lambda x: f'<span style="color:darkred;">{x}</span>' if x == 'FAIL' else x)
results_table['Compatibility'] = results_table['Compatibility'].apply(lambda x: f'<span style="color:darkred;">{x}</span>' if 'FAIL' in x else x)

# d1 plot clickable link
results_table['d1'] = results_table['Engine'].apply(lambda x: utils.d1_plots_dict(engines, 'd1_plots').get(x, None))
results_table['d1'] = results_table['d1'].apply(lambda x: utils.create_hyperlink(x))

results_md_table = results_table.to_markdown(index=False)

# save results_md_table
with open('results_compatibility_biosimulators_remote.md', 'w', encoding='utf-8') as f:
    f.write(results_md_table)