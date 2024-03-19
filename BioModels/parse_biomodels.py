#!/usr/bin/env python3

from pyneuroml.sbml import validate_sbml_files
from pyneuroml.sedml import validate_sedml_files

import requests
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
tmp_dir = "tmp1234"

#suppress stdout/err output from validation functions to make progress counter readable
suppress_stdout = True
suppress_stderr = True

fix_broken_ref = True

#skip tests that cause the script to be killed due to lack of RAM
#needs at least 8GB
skip = {}

# def get_model_identifiers():
#     '''
#     get list of all model ids
#     '''

#     request = f"{API_URL}/model/identifiers?format={out_format}"
#     if cache.mode == "reuse": return cache.get_entry(request)

#     response = requests.get(request)
#     response.raise_for_status()
#     response = response.json()['models']

#     if cache.mode == "store": cache.set_entry(request,response)
#     return response


def get_model_identifiers(request):
    '''
    get list of all model ids
    '''

    response = requests.get(request)
    response.raise_for_status()
    return response.json()['models']


# def get_model_info(model_id):

#     request = f"{API_URL}/{model_id}?format={out_format}"
#     if cache.mode == "reuse": return cache.get_entry(request)

#     response = requests.get(request)
#     response.raise_for_status()
#     response = response.json()

#     if cache.mode == "store": cache.set_entry(request,response)
#     return response

def get_model_info(request):
    'return the request in json format'
    response = requests.get(request)
    response.raise_for_status()
    return response.json()

def request_file(request):
    response = requests.get(request)
    response.raise_for_status()
    return response.content

def download_file(model_id,filename,output_file,cache):
    qfilename = urllib.parse.quote_plus(filename)

    response = cache.do_request(request_file,f'{API_URL}/model/download/{model_id}?filename={qfilename}')

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


def main():
    #caching is used to prevent the need to download the same responses from the remote server multiple times during testing
    #"off" to not use caching at all, "store" to wipe and store fresh results in the cache, "reuse" to reuse the existing cache
    cache = utils.RequestCache(mode="reuse",direc="cache")

    #accumulate results in columns defined by keys which correspond to the local variable names to be used below
    #to allow automated loading into the columns
    column_labels = "Model     |SBML     |SEDML     |broken-ref|valid-sbml|valid-sbml-units|valid-sedml|tellurium"
    column_keys  =  "model_desc|sbml_file|sedml_file|broken_ref|valid_sbml|valid_sbml_units|valid_sedml|tellurium_outcome"
    mtab = utils.MarkdownTable(column_labels,column_keys)

    #allow stdout/stderr from validation tests to be suppressed to improve progress count visibility
    sup = utils.SuppressOutput(stdout=suppress_stdout,stderr=suppress_stderr)

    #get list of all available models
    model_ids = cache.do_request(get_model_identifiers,f"{API_URL}/model/identifiers?format={out_format}")
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

        info = cache.do_request(get_model_info,f"{API_URL}/{model_id}?format={out_format}")

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
        valid_sbml = validate_sbml_files([sbml_file], strict_units=False)
        valid_sbml_units = validate_sbml_files([sbml_file], strict_units=True)
        valid_sedml = validate_sedml_files([sedml_file])
        tellurium_outcome = utils.test_engine("tellurium",sedml_file)
        sup.restore()

        mtab.append_row(locals())

        #stop matplotlib plots from building up
        matplotlib.pyplot.close()

    print() #go to next line after the progress counter

    #show total cases processed
    mtab.add_summary('model_desc',f'n={mtab.n_rows()}')

    #give failure counts
    for key in ['valid_sbml','valid_sbml_units','valid_sedml','broken_ref']:
        mtab.add_count(key,lambda x:x==False,'n_fail={count}')
        mtab.transform_column(key,lambda x:'pass' if x else 'FAIL')

    mtab.process_engine_outcomes('tellurium','tellurium_outcome')

    #write out to file
    os.chdir(starting_dir)
    with open('README.md', "w") as fout:
        mtab.write(fout)

if __name__ == "__main__":
    main()