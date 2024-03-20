#!/usr/bin/env python3

from pyneuroml.sbml import validate_sbml_files
from pyneuroml.sedml import validate_sedml_files

import re
import os
import urllib
import sys
import matplotlib

sys.path.append("..")
import utils

API_URL: str = "https://www.ebi.ac.uk/biomodels"

out_format="json"
max_count = 0 #0 for unlimited

#local temporary storage of the model files
#this is independent of caching, and still happens when caching is turned off
#this allows the model to be executed and the files manually examined etc
tmp_dir = "tmplocalfiles"

#suppress stdout/err output from validation functions to make progress counter readable
suppress_stdout = True
suppress_stderr = True

#whether to replace "model.xml" in the sedml file with the name of the actual sbml file
fix_broken_ref = True

#skip tests that cause the script to be killed due to lack of RAM
#needs at least 8GB
skip = {}

def download_file(model_id,filename,output_file,cache):
    '''
    request the given file and save it to disk
    '''

    qfilename = urllib.parse.quote_plus(filename)

    response = cache.do_request(f'{API_URL}/model/download/{model_id}?filename={qfilename}').content

    with open(output_file,"wb") as fout:
        fout.write(response)

def replace_model_xml(sedml_path,sbml_filename):
    '''
    if the SEDML refers to a generic "model.xml" file
    and the SBML file is not called this
    replace the SEDML reference with the actual SBML filename

    method used assumes 'source="model.xml"' will only
    occur in the SBML file reference
    which was true at time of testing on current BioModels release

    returns True if the SBML reference had to be fixed
    '''

    if sbml_filename == "model.xml": return False

    with open(sedml_path,encoding='utf-8') as f:
        data = f.read()

    if not 'source="model.xml"' in data: return False

    data = data.replace('source="model.xml"',f'source="{sbml_filename}"')

    with open(f'{sedml_path}',"w",encoding="utf-8") as fout:
        fout.write(data)

    return True

def format_cell(cell):
    '''
    produce the final fully formatted markdown table cell contents
    cell[0] is the boolean validation outcome
    cell[1] is the sbml/sedml filename
    cell[2] is the model_id
    '''

    cell[0] = 'pass' if cell[0] else 'FAIL'
    return f"<details><summary>{cell[0]}</summary>[{cell[1]}]({API_URL}/{cell[2]}#Files)</details>"

def main():
    '''
    download the BioModel model files, run various validation steps
    report the results as a markdown table README file with a summary row at the top
    '''

    #caching is used to prevent the need to download the same responses from the remote server multiple times during testing
    #mode="off" to disable caching, "store" to wipe and store fresh results, "reuse" to use the stored cache
    cache = utils.RequestCache(mode="reuse",direc="cache")

    #accumulate results in columns defined by keys which correspond to the local variable names to be used below
    #to allow automated loading into the columns
    column_labels = "Model     |valid-sbml|valid-sbml-units|valid-sedml|broken-ref|tellurium"
    column_keys  =  "model_desc|valid_sbml|valid_sbml_units|valid_sedml|broken_ref|tellurium_outcome"
    mtab = utils.MarkdownTable(column_labels,column_keys)

    #allow stdout/stderr from validation tests to be suppressed to improve progress count visibility
    sup = utils.SuppressOutput(stdout=suppress_stdout,stderr=suppress_stderr)

    #get list of all available models
    model_ids = cache.do_request(f"{API_URL}/model/identifiers?format={out_format}").json()['models']
    count = 0
    starting_dir = os.getcwd()

    for model_id in model_ids:
        #allow testing on a small sample of models
        if max_count > 0 and count >= max_count: break
        count += 1
        print(f"\r{count}/{len(model_ids)}       ",end='')
        if count in skip: continue

        #BIOMD ids should be the curated models
        if not 'BIOMD' in model_id: continue

        info = cache.do_request(f"{API_URL}/{model_id}?format={out_format}").json()

        #handle only single SBML files (some are Open Neural Network Exchange, or "Other" such as Docker)
        if not info['format']['name'] == "SBML": continue
        if not len(info['files']['main']) == 1: continue

        model_desc = f"[{model_id}]({API_URL}/{model_id})<br/><sup>{info['name']}</sup>"
        sbml_file = info['files']['main'][0]['name']

        #must have a SEDML file as well in order to be executed
        if not 'additional' in info['files']: continue
        sedml_file = []
        for file_info in info['files']['additional']:
            pattern = 'SED[-]?ML'
            target = f"{file_info['name']}|{file_info['description']}".upper()
            if re.search(pattern,target):
                sedml_file.append(file_info['name'])

        #require exactly one SEDML file
        if len(sedml_file) != 1: continue
        sedml_file = sedml_file[0]

        print(f'testing {sbml_file}...               ',end='')
        #make temporary downloads of the sbml and sedml files
        model_dir = os.path.join(starting_dir,tmp_dir,model_id)
        os.makedirs(model_dir,exist_ok=True)
        os.chdir(model_dir)
        download_file(model_id,sbml_file,sbml_file,cache)
        download_file(model_id,sedml_file,sedml_file,cache)

        #if the sedml file contains a generic 'source="model.xml"' replace it with the sbml filename
        if fix_broken_ref:
            broken_ref = replace_model_xml(sedml_file,sbml_file)
        else:
            broken_ref = False

        #run the validation functions on the sbml and sedml files
        sup.suppress()
        valid_sbml = [validate_sbml_files([sbml_file], strict_units=False), sbml_file, model_id] #store outcome, filename, model_id
        valid_sbml_units = validate_sbml_files([sbml_file], strict_units=True)
        valid_sedml = [validate_sedml_files([sedml_file]), sedml_file, model_id] #store outcome, filename, model_id
        tellurium_outcome = utils.test_engine("tellurium",sedml_file)
        sup.restore()

        #append the row values to their respective table columns
        mtab.append_row(locals())

        #stop matplotlib plots from building up
        matplotlib.pyplot.close()

    print() #end progress counter, go to next line of stdout

    #show total cases processed
    mtab.add_summary('model_desc',f'n={mtab.n_rows()}')

    #give failure count summaries in summary row, convert boolean values to pass/FAIL
    for key in ['valid_sbml_units','broken_ref']:
        mtab.add_count(key,lambda x:x==False,'n_fail={count}')
        mtab.transform_column(key,lambda x:'pass' if x else 'FAIL')

    #give failure count summaries in summary row, convert boolean to pass/FAIL for compound cells
    #add hideable full filenames with link to #Files tab of BioModels
    for key in ['valid_sbml','valid_sedml']:
        mtab.add_count(key,lambda x:x[0]==False,'n_fail={count}')
        mtab.transform_column(key,format_cell)

    #convert engine error messages to foldable readable form
    #calculate error category counts for summary row
    mtab.process_engine_outcomes('tellurium','tellurium_outcome')

    #write out to file
    os.chdir(starting_dir)
    with open('README.md', "w") as fout:
        mtab.write(fout)

if __name__ == "__main__":
    main()