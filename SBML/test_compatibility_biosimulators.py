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
