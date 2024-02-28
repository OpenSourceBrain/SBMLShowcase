#!/usr/bin/env python3

import requests
import re
import os
import urllib

API_URL: str = "https://www.ebi.ac.uk/biomodels"

out_format="json"

def get_model_identifiers():
    '''
    get list of all model ids
    '''

    response = requests.get(f"{API_URL}/model/identifiers?format={out_format}")
    response.raise_for_status()
    output = response.json()

    return output['models']


def get_model_info(model_id):

    response = requests.get(f"{API_URL}/{model_id}?format={out_format}")
    response.raise_for_status()
    output = response.json()

    return output


def download_file(model_id,filename,output_file):
    qfilename = urllib.parse.quote_plus(filename)
    response = requests.get(f'{API_URL}/model/download/{model_id}?filename={qfilename}')
    response.raise_for_status()

    with open(output_file,"wb") as fout:
        fout.write(response.content)

def replace_model_xml(sedml_path,sbml_filename):
    with open(sedml_path,encoding='utf-8') as f:
        data = f.read()

    data = data.replace('source="model.xml"',f'source="{sbml_filename}"')

    with open(f'{sedml_path}.fixed',"w",encoding="utf-8") as fout:
        fout.write(data)

def main():
    max_count = 0 #0 for unlimited
    tmpdir = "tmpdir1234"

    #get list of all available models
    model_ids = get_model_identifiers() 

    os.makedirs(tmpdir,exist_ok=True)
    remove_tmpdir = False

    header = "|Model|SBML|SEDML|valid-sbml|valid-sbml-units|valid-sedml|tellurium|"
    sep = "|---|---|---|---|---|---|---|"
    row = "|{model_link}<br/><sup>{model_name}</sup>|{sbml_file}|{sedml_file}| | | |"

    output = []
    output.append(header)
    output.append(sep)
    count = 0

    for model_id in model_ids:
        model_id = "BIOMD0000001027"
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
        #download_file(model_id,sbml_file,f'{tmpdir}/{model_id}/{sbml_file}')
        #download_file(model_id,sedml_file,f'{tmpdir}/{model_id}/{sedml_file}')

        #if the sedml file contains 'source="model.xml"' replace it with the sbml filename
        replace_model_xml(f'{tmpdir}/{model_id}/{sedml_file}',sbml_file)

        output.append(row.format(**locals()))

    print()

        #write out to file
    with open('README.md', "w") as fout:
        for line in output: fout.write(line+'\n')

if __name__ == "__main__":
    main()