#!/usr/bin/env python3

import requests

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


def main():
    #get list of all available models
    model_ids = get_model_identifiers() 

    max_count = 0 #0 for unlimited
    count = 0

    #models_with_sedml = []

    header = "|Model|SBML|SEDML|valid-sbml|valid-sbml-units|valid-sedml|tellurium|"
    sep = "|---|---|---|---|---|---|---|"
    row = "|{model_link}<br/><sup>{model_name}</sup>|{sbml_file}|{sedml_file}| | | |"

    output = []
    output.append(header)
    output.append(sep)

    for model_id in model_ids:
        #allow testing on a small sample of models
        if max_count > 0 and count >= max_count: break
        count +=1

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
        sbml_file = info['files']['main'][0]

        sedml_file = []
        for file_info in info['files']['additional']:
            if 'SED-ML' in file_info['name'] or 'SED-ML' in file_info['description']:
                sedml_file.append(file_info['name'])

        #require exactly one SEDML file
        if len(sedml_file) != 1: continue
        sedml_file = sedml_file[0]

        #models_with_sedml.append(model_id)

        #sedml_link = f'[{file["name"]}]({API_URL}/{model_id}#Files)' #used via locals()

        output.append(row.format(**locals()))

        # print("=======================")
        # print(f"{model_id}: {info['name']}")
        # print(f"   SBML file:  {sbml_file}")
        # print(f"   SEDML file: {sedml_file}")


    #write out to file
    with open('README.md', "w") as fout:
        for line in output: fout.write(line+'\n')

    #print("Found %i/%i containing SED-ML: %s"%(len(models_with_sedml), count, models_with_sedml))

if __name__ == "__main__":
    main()