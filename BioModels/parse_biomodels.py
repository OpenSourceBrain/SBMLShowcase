#!/usr/bin/env python3

import requests
import re
import os
import urllib
import shutil
from hashlib import sha256

API_URL: str = "https://www.ebi.ac.uk/biomodels"

out_format="json"
max_count = 0 #0 for unlimited

#"off" to not use caching at all, "setup" to wipe and store fresh results in the cache, "reuse" to reuse the existing cache
cache_mode = "setup"
cache_dir = "cache"

def setup_cache_dir():
    'wipe any existing cache directory and setup a new empty one'

    shutil.rmtree(cache_dir,ignore_errors=True)
    os.makedirs(cache_dir,exist_ok=True)


def get_cache_path(request):
    '''
    return path to cached request response
    '''

    return f"{cache_dir}/{sha256(request).hexdigest()}"


def get_cache_entry(request,encoding="UTF-8"):
    '''
    load cached response from cache_dir
    '''

    #read in binary mode
    with open(get_cache_path(request),"rb") as f:
        response = f.read()

    if encoding == None:
        #return data in raw binary form
        return response
    else:
        #decode to string
        return response.decode(encoding)
    

def set_cache_entry(request,response,encoding="UTF-8"):
    '''
    save a response to the cache
    must either provide an encoding
    or binary data as the response
    '''

    if encoding: response = response.encode(encoding)

    with open(get_cache_path(request),"wb") as fout:
        fout.write(response)


def get_model_identifiers():
    '''
    get list of all model ids
    '''

    request = f"{API_URL}/model/identifiers?format={out_format}"
    if cache_mode == "reuse": return get_cache_entry(request)

    response = requests.get()
    response.raise_for_status()
    response = response.json()['models']

    if cache_mode == "setup": set_cache_entry(request,response)
    return response


def get_model_info(model_id):

    request = f"{API_URL}/{model_id}?format={out_format}"
    if cache_mode == "reuse": return get_cache_entry(request)

    response = requests.get(request)
    response.raise_for_status()
    response = response.json()

    if cache_mode == "setup": set_cache_entry(request,response)
    return response


def download_file(model_id,filename,output_file):
    qfilename = urllib.parse.quote_plus(filename)
    request = f'{API_URL}/model/download/{model_id}?filename={qfilename}'

    if cache_mode == "reuse":
        response = get_cache_entry(request,encoding=None)
    else:
        response = requests.get(request)
        response.raise_for_status()
        response = response.content

    if cache_mode == "setup":
         set_cache_entry(request,response,encoding=None)

    with open(output_file,"wb") as fout:
        fout.write(response)

def replace_model_xml(sedml_path,sbml_filename):
    with open(sedml_path,encoding='utf-8') as f:
        data = f.read()

    data = data.replace('source="model.xml"',f'source="{sbml_filename}"')

    with open(f'{sedml_path}.fixed',"w",encoding="utf-8") as fout:
        fout.write(data)

def main():

    if cache_mode == "setup":  setup_cache_dir()

    #get list of all available models
    model_ids = get_model_identifiers() 


    header = "|Model|SBML|SEDML|valid-sbml|valid-sbml-units|valid-sedml|tellurium|"
    sep = "|---|---|---|---|---|---|---|"
    row = "|{model_link}<br/><sup>{model_name}</sup>|{sbml_file}|{sedml_file}| | | |"

    output = []
    output.append(header)
    output.append(sep)
    count = 0

    for model_id in model_ids:
        #allow testing on a small sample of models
        if max_count > 0 and count >= max_count: break
        count +=1
        print(f"\r{count}/{len(model_ids)}       ",end='')

        #BIOMD ids should be the curated models
        if not 'BIOMD' in model_id: continue

        info = get_model_info(model_id)

        #handle only single SBML files (some are Open Neural Network Exchange, or "Other" such as Docker)
        if not info['format']['name'] == "SBML": continue
        if not len(info['files']['main']) == 1: continue

        #must have a SEDML file as well in order to be executed
        if not 'additional' in info['files']: continue

        model_link = f'[{model_id}]({API_URL}/{model_id})' #used via locals()
        model_name = info['name']                          #used via locals()
        sbml_file = info['files']['main'][0]['name']

        sedml_file = []
        for file_info in info['files']['additional']:
            pattern = 'SED[-]?ML'
            target = f"{file_info['name']}|{file_info['description']}".upper()
            if re.search(pattern,target):
                sedml_file.append(file_info['name'])

        #require exactly one SEDML file
        if len(sedml_file) != 1: continue
        sedml_file = sedml_file[0]

        #make temporary downloads of the sbml and sedml files
        os.makedirs(f'{tmpdir}/{model_id}',exist_ok=True)
        download_file(model_id,sbml_file,f'{tmpdir}/{model_id}/{sbml_file}')
        download_file(model_id,sedml_file,f'{tmpdir}/{model_id}/{sedml_file}')

        #if the sedml file contains 'source="model.xml"' replace it with the sbml filename
        replace_model_xml(f'{tmpdir}/{model_id}/{sedml_file}',sbml_file)

        output.append(row.format(**locals()))

    print()

        #write out to file
    with open('README.md', "w") as fout:
        for line in output: fout.write(line+'\n')

if __name__ == "__main__":
    main()