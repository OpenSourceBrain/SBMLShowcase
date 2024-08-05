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
import argparse

parser = argparse.ArgumentParser(description='Test compatibility of different biosimulation engines')
parser.add_argument('--output-dir',action='store',default='d1_plots',help='Where to move the output pdf plots to')
args = parser.parse_args()

sbml_filepath = 'LEMS_NML2_Ex9_FN.sbml'
sedml_filepath = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing (original file)

engines = utils.engines
types_dict = utils.types_dict

engine_dict = {}

output_folder = 'output' #initial temporary output folder

for e in engines.keys():
    print('Running ' + e)
    output_dir = os.path.abspath(os.path.join(output_folder, e))
    engine_dict[e] = utils.run_biosimulators_docker(e, sedml_filepath, sbml_filepath, output_dir=output_dir)
    utils.move_d1_files(utils.find_files(output_dir, '.pdf'), e, args.output_dir)

shutil.rmtree(output_folder)

# TODO: move part that creates table to utils 
# Create a table of the results
results_table = pd.DataFrame.from_dict(engine_dict).T
results_table.columns = ['pass/FAIL', 'Error']
results_table.index.name = 'Engine'
results_table.reset_index(inplace=True)

results_table['Error'] = results_table.apply(lambda x: None if x['pass/FAIL'] == x['Error'] else x['Error'], axis=1)
results_table['pass/FAIL'] = results_table['pass/FAIL'].replace('other', 'FAIL')

results_table['Error'] = results_table['Error'].apply(lambda x: utils.ansi_to_html(x))
results_table['Error'] = results_table['Error'].apply(lambda x: utils.collapsible_content(x))

results_table['Compatibility'] = results_table['Engine'].apply(lambda x: utils.check_file_compatibility_test(x, types_dict, sbml_filepath, sedml_filepath))
results_table['Compatibility'] = results_table['Compatibility'].apply(lambda x: utils.collapsible_content(x[1], title=x[0]))
results_table['pass/FAIL'] = results_table['pass/FAIL'].apply(lambda x: f'<span style="color:darkred;">{x}</span>' if x == 'FAIL' else x)
results_table['Compatibility'] = results_table['Compatibility'].apply(lambda x: f'<span style="color:darkred;">{x}</span>' if 'FAIL' in x else x)

# d1 plot clickable link
results_table['d1'] = results_table['Engine'].apply(lambda x: utils.d1_plots_dict(engines, args.output_dir).get(x, None))
results_table['d1'] = results_table['d1'].apply(lambda x: utils.create_hyperlink(x))

results_table = results_table.to_markdown(index=False)

# save results_md_table
with open('results_compatibility_biosimulators.md', 'w', encoding='utf-8') as f:
    f.write(results_table)
