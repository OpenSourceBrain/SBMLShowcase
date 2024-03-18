#!/usr/bin/env python3

from pyneuroml.sbml import validate_sbml_files
from pyneuroml.sedml import validate_sedml_files
from pyneuroml import tellurium

import requests
import re
import os
import urllib
import shutil
from hashlib import sha256
import pickle

API_URL: str = "https://www.ebi.ac.uk/biomodels"

out_format="json"
max_count = 0 #0 for unlimited

#caching is used to prevent the need to download the same responses from the remote server multiple times during testing
#"off" to not use caching at all, "setup" to wipe and store fresh results in the cache, "reuse" to reuse the existing cache
cache_mode = "reuse"
cache_dir = "cache"

#local temporary storage of the model files
#this is independent of caching, and still happens when caching is turned off
#this allows the model to be executed and the files manually examined etc
tmp_dir = "tmp1234"

#strings to use to represent passed and failed tests
okay = "pass"
fail = "FAIL"
def pass_or_fail(result):
    '''
    convert True into "pass" and False into "fail"
    as otherwise it's not obvious in the table what True and False mean
    '''
    global okay,fail

    return okay if result else fail

def setup_cache_dir():
    'wipe any existing cache directory and setup a new empty one'

    shutil.rmtree(cache_dir,ignore_errors=True)
    os.makedirs(cache_dir,exist_ok=True)


def get_cache_path(request):
    '''
    return path to cached request response
    '''

    return f"{cache_dir}/{sha256(request.encode('UTF-8')).hexdigest()}"


def get_cache_entry(request):
    '''
    load cached response from cache_dir
    note this should only be used in a context where you trust the integrity of the cache files
    due to using pickle
    note also: no handling of cache misses yet implemented
    '''

    with open(get_cache_path(request),"rb") as f:
        return pickle.load(f)
    

def set_cache_entry(request,response):
    '''
    save a response to the cache
    '''

    with open(get_cache_path(request),"wb") as fout:
        pickle.dump(response,fout)


def get_model_identifiers():
    '''
    get list of all model ids
    '''

    request = f"{API_URL}/model/identifiers?format={out_format}"
    if cache_mode == "reuse": return get_cache_entry(request)

    response = requests.get(request)
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
        response = get_cache_entry(request)
    else:
        response = requests.get(request)
        response.raise_for_status()
        response = response.content

    if cache_mode == "setup":
         set_cache_entry(request,response)

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

class MarkdownTable:
    '''
    helper class to accumulate rows of data with a header and optional summary row
    to be written to file as a markdown table
    '''
    def __init__(self,labels:str,keys:str,splitter='|'):
        'specify column headers and variable names'
        self.labels = [x.strip() for x in labels.split(splitter)]
        self.keys = [x.strip() for x in keys.split(splitter)]
        assert len(self.keys) == len(self.labels)
        self.data = {key:[] for key in self.keys}
        self.summary = None

    def append_row(self,vars):
        'ingest the next row from a variables dict (eg locals())'
        for key in self.keys:
            self.data[key].append(vars[key])

    def get_column(self,key):
        'return the named column'
        return self.data[key]
    
    def __getitem__(self,key):
        'convenience wrapper to allow square brackets access to columns'
        return self.get_column(key)
    
    def n_rows(self):
        'return number of data rows'
        return len(self.data[self.keys[0]])

    def n_cols(self):
        'return number of data columns'
        return len(self.data)

    def add_summary(self,key,value):
        'fill in the optional summary cell for the named column'
        if not self.summary:
            self.summary = {key:"" for key in self.keys}

        self.summary[key] = value

    def add_count(self,key,func,format='n={count}'):
        'add a basic summary counting how many times the function is true'
        count = len([ x for x in self.data[key] if func(x) ])

        self.add_summary(key,format.format(count=count))

    def transform_column(self,key,func):
        'pass all column values through a function'
        for i in range(len(self.data[key])):
            self.data[key][i] = func(self.data[key][i])

    def write(self,fout,sep='|',end='\n'):
        'write the markdown table to file'
        fout.write(sep + sep.join(self.labels) + sep + end)
        fout.write(sep + sep.join(['---' for x in self.labels]) + sep + end)
        if self.summary:
            fout.write(sep + sep.join([ str(self.summary[key]) for key in self.keys ]) + sep + end)

        for i in range(self.n_rows()):
            fout.write(sep + sep.join([ str(self.data[key][i]) for key in self.keys ])  + sep + end)


def main():
    #wipe any existing cache entries
    if cache_mode == "setup":  setup_cache_dir()

    #accumulate results in columns defined by keys which correspond to the local variable names to be used below
    #to allow automated loading into the columns
    column_labels = "Model     |SBML     |SEDML     |broken-ref|valid-sbml|valid-sbml-units|valid-sedml|tellurium"
    column_keys  =  "model_desc|sbml_file|sedml_file|broken_ref|valid_sbml|valid_sbml_units|valid_sedml|tellurium_outcome"

    mtab = MarkdownTable(column_labels,column_keys)

    #get list of all available models
    model_ids = get_model_identifiers() 
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

        #make temporary downloads of the sbml and sedml files
        os.makedirs(f'{tmp_dir}/{model_id}',exist_ok=True)
        download_file(model_id,sbml_file,f'{tmp_dir}/{model_id}/{sbml_file}')
        download_file(model_id,sedml_file,f'{tmp_dir}/{model_id}/{sedml_file}')

        #if the sedml file contains a generic 'source="model.xml"' replace it with the sbml filename
        broken_ref = replace_model_xml(f'{tmp_dir}/{model_id}/{sedml_file}',sbml_file) #used via locals()

        #run the validation functions on the sbml and sedml files
        valid_sbml = validate_sbml_files([f'{tmp_dir}/{model_id}/{sbml_file}'], strict_units=False)
        valid_sbml_units = validate_sbml_files([f'{tmp_dir}/{model_id}/{sbml_file}'], strict_units=True)
        valid_sedml = validate_sedml_files([f'{tmp_dir}/{model_id}/{sedml_file}'])

        tellurium_outcome = 'stub'

        mtab.append_row(locals())

    print() #go to next line after the progress counter

    #show total cases processed
    mtab.add_summary('model_desc',f'n={mtab.n_rows()}')

    #give failure counts
    for key in ['valid_sbml','valid_sbml_units','valid_sedml','broken_ref']:
        mtab.add_count(key,lambda x:x==False,'n_fail={count}')
        mtab.transform_column(key,lambda x:'pass' if x else 'FAIL')

    #write out to file
    with open('README.md', "w") as fout:
        mtab.write(fout)

if __name__ == "__main__":
    main()