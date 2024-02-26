
import requests

API_URL: str = "https://www.ebi.ac.uk/biomodels"

out_format="json"

def get_model_identifiers():

    response = requests.get(API_URL + "/model/identifiers?format=" + out_format)
    response.raise_for_status()
    output = response.json()

    return output


def get_model_info(model_id):

    response = requests.get(API_URL + "/"+model_id+"?format=" + out_format)
    response.raise_for_status()
    output = response.json()

    return output



if __name__ == "__main__":

    model_ids = get_model_identifiers()['models'] 

    max_count = 3000
    count = 0

    with_sedml = []

    header = "|Model|valid-sbml|valid-sbml-units|SED-ML|"
    sep = "|---|---|---|---|"
    row = "|{model_link}<br/><sup>{model_name}</sup>|???|???|{sedml_link}|"

    with open('README.md', "w") as fout:
        output = []
        output.append(header)
        output.append(sep)

        for model_id in model_ids:
            if count<max_count:
                if 'BIOMD' in model_id:
                    model_link = f'[{model_id}](https://www.ebi.ac.uk/biomodels/{model_id})'
                    info = get_model_info(model_id)
                    model_name = info['name']
                    print("=======================")
                    print(f"  {model_id}: {info['name']}")
                    #print(info.keys())
                    for file in info['files']['main']:
                        print('   %s'%file)
                    if 'additional' in info['files']:
                        for file in info['files']['additional']:
                            if 'SED-ML' in file['name'] or 'SED-ML' in file['description']:
                                with_sedml.append(model_id)
                                print('   - SED-ML: %s'%file)

                                sedml_link = f'[{file["name"]}](https://www.ebi.ac.uk/biomodels/{model_id}#Files)'
                                output.append(row.format(**locals()))

                    count +=1 
        
        for line in output: fout.write(line+'\n')

    print("Found %i/%i containing SED-ML: %s"%(len(with_sedml), count, with_sedml))