#!/usr/bin/env python3

import pyneuroml.sbml #for validate_sbml_files
import pyneuroml.sedml #for validate_sedml_files

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

    returns True if the SBML reference already seemed valid
    '''

    if sbml_filename == "model.xml": return True

    with open(sedml_path,encoding='utf-8') as f:
        data = f.read()

    if not 'source="model.xml"' in data: return True

    data = data.replace('source="model.xml"',f'source="{sbml_filename}"')

    with open(f'{sedml_path}',"w",encoding="utf-8") as fout:
        fout.write(data)

    return False

def validate_sbml_file(model_id,mtab,info,cache,sup):
    '''
    tasks relating to validating the SBML file
    return None to indicate aborting any further tests on this model
    otherwise return the SBML filename
    '''

    #handle only single SBML files
    if not info['format']['name'] == "SBML":
        mtab['valid_sbml'] = ['NonSBML', f"{info['format']['name']}:{info['files']['main']}"]
        return None

    if len(info['files']['main']) > 1:
        mtab['valid_sbml'] = ['MultipleSBMLs',f"{info['files']['main']}"]
        return None

    if len(info['files']['main']) < 1:
        mtab['valid_sbml'] = ['NoSBMLs',f"{info['files']['main']}"]
        return None

    #download the sbml file
    sbml_file = info['files']['main'][0]['name']
    try:
        download_file(model_id,sbml_file,sbml_file,cache)
    except Exception as e:
        mtab['valid_sbml'] = ['DownloadFail',f"{sbml_file} {e}"]
        return None

    #
    #    return f"<details><summary>summary</summary>details</details>"

    #validate the sbml file
    sup.suppress() #suppress validation warning/error messages  
    valid_sbml = pyneuroml.sbml.validate_sbml_files([sbml_file], strict_units=False)
    valid_sbml_units = pyneuroml.sbml.validate_sbml_files([sbml_file], strict_units=True)
    sup.restore()

    mtab['valid_sbml'] = ['pass' if valid_sbml else 'FAIL', f'[{sbml_file}]({API_URL}/{model_id}#Files)']
    mtab['valid_sbml_units'] = ['pass' if valid_sbml_units else 'FAIL', None]

    return sbml_file

def validate_sedml_file(model_id,mtab,info,cache,sup,sbml_file):
    '''
    tasks relating to validating the SEDML file
    return None to indicate aborting any further tests on this model
    otherwise return the SEDML filename
    '''

    #must have a SEDML file as well in order to be executed
    if not 'additional' in info['files']:
        mtab['valid_sedml'] = f"NoSEDML"
        return None

    sedml_file = []
    for file_info in info['files']['additional']:
        pattern = 'SED[-]?ML'
        target = f"{file_info['name']}|{file_info['description']}".upper()
        if re.search(pattern,target):
            sedml_file.append(file_info['name'])

    #require exactly one SEDML file
    if len(sedml_file) == 0:
        mtab['valid_sedml'] = "NoSEDML"
        return None

    if len(sedml_file) > 1:
        mtab['valid_sedml'] = ["MultipleSEDMLs",f"{sedml_file}"]
        return None

    #download sedml file
    sedml_file = sedml_file[0]
    try:
        download_file(model_id,sedml_file,sedml_file,cache)
    except:
        mtab['valid_sedml'] = ["DownloadFail",f"{sedml_file}"]
        return None

    #if the sedml file contains a generic 'source="model.xml"' replace it with the sbml filename
    if fix_broken_ref:
        broken_ref = replace_model_xml(sedml_file,sbml_file)
        mtab['broken_ref'] = 'pass' if broken_ref else 'FAIL'
    else:
        mtab['broken_ref'] = 'NA'

    sup.suppress()
    valid_sedml = pyneuroml.sedml.validate_sedml_files([sedml_file])
    sup.restore()
    mtab['valid_sedml'] = ['pass' if valid_sedml else 'FAIL', f'[{sedml_file}]({API_URL}/{model_id}#Files)']

    return sedml_file

def format_cell(key,cell):
    '''
    produce the final fully formatted markdown table cell contents
    '''

    if type(cell) == list:
        assert len(cell) == 2
        if cell[1]:
            summary = utils.safe_md_string(cell[1])
            return f"<details><summary>{cell[0]}</summary>{summary}</details>"
        else:
            return cell[0]
        
    return str(cell)

def main():
    '''
    download the BioModel model files, run various validation steps
    report the results as a markdown table README file with a summary row at the top
    '''

    #caching is used to prevent the need to download the same responses from the remote server multiple times during testing
    #mode="off" to disable caching, "store" to wipe and store fresh results, "reuse" to use the stored cache
    cache = utils.RequestCache(mode="auto",direc="cache")

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
        print(f"\r{model_id} {count}/{len(model_ids)}       ",end='')

        #only process curated models
        #BIOMD ids should be the curated models
        if not 'BIOMD' in model_id:
            continue

        #skip if on the list to be skipped
        if count in skip or model_id in skip:
            continue

        #from this point the model will create an output row even if not all tests are run
        mtab.new_row(missing='NA') #append empty placeholder row
        info = cache.do_request(f"{API_URL}/{model_id}?format={out_format}").json()
        mtab['model_desc'] = f"[{model_id}]({API_URL}/{model_id})<br/><sup>{info['name']}</sup>"

        #make temporary downloads of the sbml and sedml files
        model_dir = os.path.join(starting_dir,tmp_dir,model_id)
        os.makedirs(model_dir,exist_ok=True)
        os.chdir(model_dir)

        #sbml file validation tasks, includes downloading a local copy
        sbml_file = validate_sbml_file(model_id,mtab,info,cache,sup)
        if not sbml_file: continue # no further tests possible

        sedml_file = validate_sedml_file(model_id,mtab,info,cache,sup,sbml_file)
        if not sedml_file: continue # no further tests possible

        #run the validation functions on the sbml and sedml files
        print(f'testing {sbml_file}...               ',end='')
        sup.suppress()
        mtab['tellurium_outcome'] = utils.test_engine("tellurium",sedml_file)
        sup.restore()

        #stop matplotlib plots from building up
        matplotlib.pyplot.close()

    print() #end progress counter, go to next line of stdout

    #show total cases processed
    mtab.add_summary('model_desc',f'n={mtab.n_rows()}')

    #count occurrences of each cell value, convert to final form
    for key in ['valid_sbml','valid_sbml_units','valid_sedml','broken_ref']:
        mtab.simple_summary(key)
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