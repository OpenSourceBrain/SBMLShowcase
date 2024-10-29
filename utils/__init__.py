import shutil
import os
import pickle
import hashlib
import sys
from dataclasses import dataclass
from pyneuroml import tellurium
import re
import requests
from collections import defaultdict
from pathlib import Path
import random
from pymetadata.console import console
from pymetadata import omex
import docker
import yaml
import libsbml
import libsedml
import tempfile
import glob
from pyneuroml import biosimulations
import pandas as pd
from requests.exceptions import HTTPError 

ENGINES = {
    'amici': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_AMICI/',
        'status': ""
    },
    'brian2': {
        'formats': [('nml', 'sedml'), ('lems', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_pyNeuroML/',
        'status': ""
    },
    'bionetgen': {
        'formats': [('bngl', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_BioNetGen/',
        'status': ""
    },
    'boolnet': {
        'formats': [('sbmlqual', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_BoolNet/',
        'status': ""
    },
    'cbmpy': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_CBMPy/',
        'status': ""
    },
    'cobrapy': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_COBRApy/',
        'status': "Only allows steady state simulations"
    },
    'copasi': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_COPASI/',
        'status': ""
    },
    'gillespy2': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_GillesPy2/',
        'status': ""
    },
    'ginsim': {
        'formats': [('sbmlqual', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_GINsim/',
        'status': ""
    },
    'libsbmlsim': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_LibSBMLSim/',
        'status': ""
    },
    'masspy': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_MASSpy/',
        'status': ""
    },
    'netpyne': {
        'formats': [('nml', 'sedml'), ('lems', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_pyNeuroML/',
        'status': ""
    },
    'neuron': {
        'formats': [('nml', 'sedml'), ('lems', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_pyNeuroML/',
        'status': ""
    },
    'opencor': {
        'formats': [('cellml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_OpenCOR/',
        'status': ""
    },
    'pyneuroml': {
        'formats': [('nml', 'sedml'), ('lems', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_pyNeuroML/',
        'status': ""
    },
    'pysces': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_PySCeS/',
        'status': ""
    },
    'rbapy': {
        'formats': [('rbapy', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_RBApy/',
        'status': ""
    },
    'smoldyn': {
        'formats': [('smoldyn', 'sedml')],
        'url': 'https://smoldyn.readthedocs.io/en/latest/python/api.html#sed-ml-combine-biosimulators-api',
        'status': ""
    },
    'tellurium': {
        'formats': [('sbml', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_tellurium/',
        'status': ""
    },
    'vcell': {
        'formats': [('sbml', 'sedml'),('bngl', 'sedml')],
        'url': 'https://github.com/virtualcell/vcell',
        'status': ""
    },
    'xpp': {
        'formats': [('xpp', 'sedml')],
        'url': 'https://docs.biosimulators.org/Biosimulators_XPP/',
        'status': ""
    }
}


TYPES = {
                'sbml':'SBML',\
                'sedml':'SED-ML',\
                'nml':'NeuroML',\
                'lems':'LEMS',\
                'sbmlqual':'SBML-qual',\
                'bngl':'BNGL',\
                'rbapy':'RBApy',\
                'xpp':'XPP',\
                'smoldyn':'Smoldyn',\
                'cellml':'CellML',\
                'xml':'XML'\
             }

# define the column headers for the markdown table
ERROR = 'Error'
PASS_FAIL = 'pass / FAIL'
TYPE = 'Type'
COMPAT = 'Compatibility'
D1 = 'd1'
ENGINE = 'Engine'

#define error categories for detailed error counting per engine
# (currently only tellurium)
# key is the tag/category used to report the category, value is a regex matching the error message
# see MarkdownTable.process_engine_outcomes
error_categories=\
{
    "tellurium":
        {
            "algebraic":"^Unable to support algebraic rules.",
            "delay":"^Unable to support delay differential equations.",
            "ASTNode":"^Unknown ASTNode type of",
            "stochiometry":"^Mutable stochiometry for species which appear multiple times in a single reaction",
            "float":"^'float' object is not callable",
            "SpeciesRef":"is not a named SpeciesReference",
            "reset":"reset",
            "SEDMLfile":"^failed to validate SEDML file",
            "NoSBMLelement":"^No sbml element exists",
            "CV_ERR_FAILURE":"CV_ERR_FAILURE",
            "CV_TOO_MUCH_WORK":"CV_TOO_MUCH_WORK",
            "CV_CONV_FAILURE":"CV_CONV_FAILURE",
            "CV_ILL_INPUT":"CV_ILL_INPUT",
            "OutOfRange":"list index out of range",
        },
}

def get_entry_format(file_path, file_type):
    '''
    Get the entry format for a file.

    Args:
        file_path (:obj:`str`): path to the file
        file_type (:obj:`str`): type of the file

    Returns:
        :obj:`str`: entry format
    '''

    if file_type == 'SBML':
        file_l = libsbml.readSBML(file_path).getLevel()
        file_v = libsbml.readSBML(file_path).getVersion()
    elif file_type == 'SEDML':
        file_l = libsedml.readSedML(file_path).getLevel()
        file_v = libsedml.readSedML(file_path).getVersion()
    else:
        raise ValueError(f"Invalid file type: {file_type}")

    file_entry_format = f"{file_type}_L{file_l}V{file_v}"
    entry_formats = [f.name for f in omex.EntryFormat]
    if file_entry_format not in entry_formats:
        file_entry_format = file_type

    return file_entry_format


def add_xmlns_sbml_attribute(sedml_filepath, sbml_filepath, output_filepath=None):
    '''
    add an xmlns:sbml attribute to the sedml file that matches the sbml file
    raise an error if the attribute is already present
    output fixed file to output_filepath which defaults to sedml_filepath
    '''

    # read the sedml file as a string
    with open(sedml_filepath, 'r') as file:
        sedstr = file.read()

    m = re.search(r'<sedML[^>]*>', sedstr)

    if m == None:
        raise ValueError(f'Invalid SedML file: main <sedML> tag not found in {sedml_filepath}')

    # read the sbml file as a string to add the xmlns attribute if it is missing
    if "xmlns:sbml" in m.group():
        raise ValueError(f'xmlns:sbml attribute already present in file {sedml_filepath}')

    with open(sbml_filepath, 'r') as file:
        sbml_str = file.read()

    sbml_xmlns = re.search(r'xmlns="([^"]*)"', sbml_str).group(1)
    missing_sbml_attribute = 'xmlns:sbml="' + sbml_xmlns + '"'

    sedstr = re.sub(r'<sedML ', r'<sedML ' + missing_sbml_attribute + ' ', sedstr)

    if output_filepath == None:
        output_filepath = sedml_filepath

    with open(output_filepath,"w") as fout:
        fout.write(sedstr)


def xmlns_sbml_attribute_missing(sedml_filepath):
    '''
    report True if the xmlns:sbml attribute is missing from the main sedml tag
    '''

    with open(sedml_filepath, 'r') as file:
        sedstr = file.read()

    m = re.search(r'<sedML[^>]*>', sedstr)

    if m == None:
        raise ValueError(f'Invalid SedML file: main <sedML> tag not found in {sedml_filepath}')
    
    if "xmlns:sbml" not in m.group():
        return True
    else:
        return False

def get_temp_file():
    '''
    create a temporary filename in the current working directory
    '''
    return f"tmp{random.randrange(1000000)}"

def create_omex(sedml_filepath, sbml_filepath, omex_filepath=None, silent_overwrite=True, add_missing_xmlns=True):
    '''
    wrap a sedml and an sbml file in a combine archive omex file
    overwrite any existing omex file
    '''

    #provide an omex filepath if not specified
    if not omex_filepath:
        if sedml_filepath.endswith('.sedml'):
            omex_filepath = Path(sedml_filepath[:-6] + '.omex')
        elif sedml_filepath.endswith('.xml'):
            omex_filepath = Path(sedml_filepath[:-4] + '.omex')
        else:
            omex_filepath = Path(sedml_filepath+'.omex')

    #suppress pymetadata "file exists" warning by preemptively removing existing omex file
    if os.path.exists(omex_filepath) and silent_overwrite:
        os.remove(omex_filepath)

    tmp_sedml_filepath = None
    if add_missing_xmlns:
        if xmlns_sbml_attribute_missing(sedml_filepath):
            #create a temporary sedml file with the missing attribute added
            tmp_sedml_filepath = get_temp_file()
            add_xmlns_sbml_attribute(sedml_filepath, sbml_filepath, tmp_sedml_filepath)
            sedml_filepath = tmp_sedml_filepath

    sbml_file_entry_format = get_entry_format(sbml_filepath, 'SBML')
    sedml_file_entry_format = get_entry_format(sedml_filepath, 'SEDML')

    #wrap sedml+sbml files into an omex combine archive
    om = omex.Omex()
    om.add_entry(
        entry = omex.ManifestEntry(
            location = sedml_filepath,
            format = getattr(omex.EntryFormat, sedml_file_entry_format),
            master = True,
        ),
        entry_path = Path(os.path.basename(sedml_filepath))
    )
    om.add_entry(
        entry = omex.ManifestEntry(
            location = sbml_filepath,
            format = getattr(omex.EntryFormat, sbml_file_entry_format),
            master = False,
        ),
        entry_path = Path(os.path.basename(sbml_filepath))
    )
    om.to_omex(Path(omex_filepath))

    if tmp_sedml_filepath:
        os.remove(tmp_sedml_filepath)

    return omex_filepath

def read_log_yml(log_filepath):
    '''
    read the log YAML file if it exists
    return the exception message as a string
    '''
    if not os.path.isfile(log_filepath):
        return None
    with open(log_filepath) as f:
        ym = yaml.safe_load(f)
    return ym['exception']['message']

def find_files(directory, extension):
    files = glob.glob(f"{directory}/**/*{extension}", recursive=True)
    return files

def move_d1_files(file_paths, plot_dir='d1_plots'):
    for fpath in file_paths:
        # find engine.keys() in the file path and asign to engine
        engine = next((e for e in ENGINES.keys() if e in fpath), 'unknown')
        new_file_path = os.path.join(plot_dir, f'{engine}_{os.path.basename(fpath)}')
        if not os.path.exists(plot_dir): os.makedirs(plot_dir, exist_ok=True)
        if os.path.exists(new_file_path): os.remove(new_file_path)
        print(f'Moving {fpath} to {new_file_path}')
        shutil.move(fpath, new_file_path)

def find_file_in_dir(file_name, directory):
    """
    Searches for a specific file in a given directory and its subdirectories.

    Parameters:
    file_name (str): The name of the file to search for.
    directory (str): The directory to search in.

    Returns:
    str: The path of the found file. If the file is not found, returns None.
    """

    list_of_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file == file_name:
                file_path = os.path.join(root, file)
                list_of_files.append(file_path)
    return list_of_files


# write definition to create d1 plots dict
def d1_plots_dict(d1_plots_path='d1_plots'):
    """
    Create a dictionary with engine names as keys and d1 plot paths as values.
    """
    d1_plots = find_files(d1_plots_path, '.pdf')
    # to fix broken links in output table after changing the file structure, remove the first two parts of the path
    d1_plots = [os.path.join(*Path(d1_plot).parts[1:]) for d1_plot in d1_plots]
    d1_plots_dict = {e: d1_plot for e in ENGINES.keys() for d1_plot in d1_plots if e in d1_plot}
    
    return d1_plots_dict


def create_hyperlink(file_path, title=None):
    """
    Create a hyperlink to a file or folder. If the path is None, return None.
    Title is the basename of the path.
    """
    if file_path:
        if title is None:
            title = os.path.basename(file_path)
        return f'<a href="{file_path}">{title}</a>'
    else:
        return None
    

def ansi_to_html(text):
    if text != None:
        text_message = re.findall(r'"([^"]*)"', text) 
        if len(text_message) > 0:
            text = text_message
            text = bytes(text[0], "utf-8").decode("unicode_escape")
        elif 'The COMBINE/OMEX did not execute successfully:' in text:
            text = text # to deal with remote error message
        else:
            text = text.replace('|', '')
            return text

        text = text.replace('|', '')

        # # for any text with "<*>" remove "<" as well as ">" but leave wildcard text *
        text = re.sub(r'<([^>]*)>', r'\1', text)

        # replace color codes with html color codes
        text = text.replace("\x1b[33m",'<span style="color:darkorange;">')
        text = text.replace("\x1b[31m",'<span style="color:red;">')

        # # remove .\x1b[0m
        text = text.replace("\x1b[0m", "")

        # find first "." or ":" after "<span*" and add "</span>"after it
        pattern = r'(<span style="[^"]*">[^.:]*)([.:])'
        replacement = r'\1\2</span>'
        text = re.sub(pattern, replacement, text, count=1)

        # bullet points and new lines
        text = text.replace('\r\n  - ', '</li><li>')
        text = text.replace('\r\n', '<br>')
        text = text.replace('\n', '<br>') 

        # BioSimulatorsWarning:  two <br> tags after
        text = text.replace('BioSimulatorsWarning:', '<br><br>BioSimulatorsWarning:<br><br>')
        text = text.replace('warnings.warn(termcolor.colored(message, Colors.warning.value), category)', '<br>')

        # if text includes The COMBINE/OMEX did not execute successfully: make everyhting from that point red
        text = text.replace('The COMBINE/OMEX did not execute successfully:', '<span style="color:red;">The COMBINE/OMEX did not execute successfully:')
    return text

def display_error_message(error_message):
    if error_message != None:
        display_markdown(f'{error_message}', raw=True)
    return error_message

def check_file_compatibility_test(engine, model_filepath, experiment_filepath):
    '''
    Check if the file extensions suggest the file types are compatible with the engine.
    This is done by comparing the file extensions of the model and experiment files with the file types supported by the engine.
    For SED-ML files, the expected file extension is '.sedml'. For SBML files, the expected file extension is '.sbml'.
    '''
    input_filetypes_tuple = get_filetypes(model_filepath, experiment_filepath)
    engine_filetypes_tuple_list = ENGINES[engine]['formats']
    flat_engine_filetypes_tuple_list = [item for sublist in engine_filetypes_tuple_list for item in sublist if sublist != 'unclear']
    compatible_filetypes = [TYPES[i] for i in flat_engine_filetypes_tuple_list if i in list(TYPES.keys())]

    if input_filetypes_tuple in engine_filetypes_tuple_list:
        file_types = [TYPES[i] for i in input_filetypes_tuple]
        return 'pass', (f"The file extensions {input_filetypes_tuple} suggest the input file types are '{file_types}'. {compatible_filetypes} are compatible with {engine}")
    if 'xml' in input_filetypes_tuple:
        return 'unsure', (f"The file extensions of the input files are '{input_filetypes_tuple}'. These may be compatible with {engine}. {compatible_filetypes} are compatible with {engine}")
    else:
        return 'FAIL', (f"The file extensions {input_filetypes_tuple} suggest the input file types are not compatibe with {engine}. {compatible_filetypes} are compatible with {engine}")
    

def collapsible_content(content, title='Details'):
    """
    Create a collapsible content section in markdown format
    
    Input: content, title
    """
    if content:
        return f'<details><summary>{title}</summary>{content}</details>'
    else:
        return None
    
def get_filetypes(model_filepath, simulation_filepath):
    """
    Get the filetypes of the model and simulation files

    Input: model_filepath, simulation_filepath
    Output: tuple of filetypes
    """
    if model_filepath.endswith(".sbml") and simulation_filepath.endswith(".sedml"):
        filetypes = ('sbml', 'sedml')
    elif model_filepath.endswith(".xml") and simulation_filepath.endswith(".xml"):
        filetypes = ('xml', 'xml')
    elif model_filepath.endswith(".xml") and simulation_filepath.endswith(".sedml"):
        filetypes = ('xml', 'sedml')
    elif model_filepath.endswith(".sbml") and simulation_filepath.endswith(".xml"):
        filetypes = ('sbml', 'xml')
    else:
        filetypes = "other"
    return filetypes

def delete_output_folder(output_dir):
    '''
    # Delete the output folder and its contents
    '''
    for file_name in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def run_biosimulators_remote(engine,sedml_filepath,sbml_filepath):
    '''
    put the sedml and sbml file into an omex archive
    run it remotely using biosimulators
    '''

    #put the sedml and sbml into a combine archive
    omex_filepath = create_omex(sedml_filepath,sbml_filepath)
    omex_file_name = os.path.basename(omex_filepath)

    # get the version of the engine
    engine_version = biosimulations.get_simulator_versions(engine)

    sim_dict = {
                "name": "test",
                "simulator": engine,
                "simulatorVersion": engine_version[engine][-1], # get the latest version
                "cpus": 1,
                "memory": 8,
                "maxTime": 20,
                "envVars": [],
                "purpose": "academic",
                "email": "",
                }

    res = biosimulations.submit_simulation_archive(\
        archive_file=omex_file_name,\
        sim_dict=sim_dict)
    
    download_url = res["download"]
    
    return download_url

def get_remote_results(engine, download_link, output_dir='remote_results'):

    filepath_results = download_file_from_link(engine, download_link)
    extract_dir = os.path.join(os.getcwd(), output_dir, engine)
    shutil.unpack_archive(filepath_results, extract_dir=extract_dir)
    os.remove(filepath_results)

    return extract_dir

def rename_files_in_extract_dir(extract_dir, engine):
    
    # find the log.yml file in the extracted directory
    log_yml_path = find_file_in_dir('log.yml', extract_dir)[0]
    with open(log_yml_path) as f:
        log_yml_dict = yaml.safe_load(f)
    
    # rename log.yml file to '{engine}_log.yml'
    new_file_name = f'{engine}_log.yml'
    root = os.path.dirname(log_yml_path)
    new_file_path = os.path.join(root, new_file_name)
    if os.path.exists(new_file_path):
        os.remove(new_file_path)
    os.rename(log_yml_path, new_file_path)
    
    return extract_dir


def run_biosimulators_docker(engine,sedml_filepath,sbml_filepath,output_dir='output',error_categories=error_categories,chown_outputs=True):
    '''
    put the sedml and sbml file into an omex archive
    run it locally using a biosimulators docker
    categorise an error message in the log file
    '''

    #put the sedml and sbml into a combine archive
    omex_filepath = create_omex(sedml_filepath,sbml_filepath)
    error_str = None

    try:
        biosimulators_core(engine,omex_filepath,output_dir=output_dir)
    except Exception as e:
        #capture the error as a string which won't break markdown tables 
        # error_str = safe_md_string(e)
        error_str = str(e)

    #ensure outputs are owned by the user
    if 'getuid' in dir(os) and chown_outputs:
        uid = os.getuid()
        gid = os.getgid()
        os.system(f'sudo chown -R {uid}:{gid} {output_dir}')

    if not error_str: return "pass"

    # #try to load the cleaner error message from the log.yml file
    log_str = read_log_yml(os.path.join(os.path.dirname(omex_filepath),"log.yml"))

    if log_str:
        error_str = str(log_str)
    # if log_str:
    #     error_str = safe_md_string(log_str)

    #categorise the error string
    if engine in error_categories:
        for tag in error_categories[engine]:
            if re.search(error_categories[engine][tag],error_str):
                return [tag,f"```{error_str}```"]
    
    return ["other",f"```{error_str}```"]

def biosimulators_core(engine,omex_filepath,output_dir=None):
    '''
    run the omex file using biosimulators
    calls biosimulators via docker locally
    assumes local docker is setup
    engine can be any string that matches a biosimulators docker "URI":
    ghcr.io/biosimulators/{engine}

    omex_filepath: the OMEX file to run
    output_dir: folder to write the simulation outputs to
    '''

    #directory containing omex file needs mapping into the container as the input folders
    omex_dir = os.path.dirname(os.path.abspath(omex_filepath))
    omex_file = os.path.basename(os.path.abspath(omex_filepath))
    mount_in = docker.types.Mount("/root/in",omex_dir,type="bind",read_only=True)

    #we want the output folder to be different to the input folder
    #to avoid the "file already exists" type error
    if not output_dir:
        output_dir = os.path.join(omex_dir,'output')

    os.makedirs(output_dir,exist_ok=True)

    mount_out = docker.types.Mount("/root/out",output_dir,type="bind")
    client = docker.from_env()
    client.containers.run(f"ghcr.io/biosimulators/{engine}",
                        mounts=[mount_in,mount_out],
                        command=f"-i /root/in/{omex_file} -o /root/out",
                        auto_remove=True)

def test_engine(engine,filename,error_categories=error_categories):
    '''
    test running the file with the given engine
    return category tagged error message, or "pass" if no error was raised
    '''

    unknown_engine = False
    try:
        if engine == "tellurium":
            tellurium.run_from_sedml_file([filename],["-outputdir","none"])
            return "pass" #no errors
        #elif engine == "some_other_engine":
        #    #run it here
        #    return "pass"
        else:
            unknown_engine = True
    except Exception as e:
        #return error object
        error_str = safe_md_string(e)

    if unknown_engine:
        raise RuntimeError(f"unknown engine {engine}")

    for tag in error_categories[engine]:
        if re.search(error_categories[engine][tag],error_str):
            return [tag,f"```{error_str}```"]
    
    return ["other",f"```{error_str}```"]

@dataclass
class SuppressOutput:
    '''
    redirect stdout and/or stderr to os.devnull
    stdout: whether to suppress stdout
    stderr: whether to suppress stderr
    '''

    stdout: bool = False
    stderr: bool = False

    def suppress(self):
        'begin to suppress output(s)'
        if self.stdout:
            self.orig_stdout = sys.stdout
            sys.stdout = open(os.devnull,"w")
        if self.stderr:
            self.orig_stderr = sys.stderr
            sys.stderr = open(os.devnull,"w")

    def restore(self):
        'restore output(s)'
        if self.stdout:
            sys.stdout.close()
            sys.stdout = self.orig_stdout
        if self.stderr:
            sys.stderr.close()
            sys.stderr = self.orig_stderr


class RequestCache:
    '''
    caching is used to prevent the need to download the same responses from the remote server multiple times during testing
    currently no handling of unexpected cache misses
    '''

    def __init__(self,mode="off",direc="cache"):
        '''
        mode:
            "off" to disable caching (does not wipe any existing cache data)
            "store" to wipe and store fresh results in the cache
            "reuse" to only use existing cache files
            "auto" to download only if missing
            could also implement "auto" mode that only downloads on a cache miss
        direc: the directory used to store the cache
        '''
        self.mode = mode

        #store absolute cache dir path to ensure it is found regardless of current directory
        self.absolute_dir = os.path.join(os.getcwd(),direc)

        if mode == "store": self.wipe()


    def wipe(self):
        'wipe any existing cache directory and setup a new empty one'

        shutil.rmtree(self.absolute_dir,ignore_errors=True)
        os.makedirs(self.absolute_dir,exist_ok=True)


    def get_path(self,request=None):
        '''
        return path to cached request response
        or just the cache base directory for a null request
        '''

        return os.path.join(f"{self.absolute_dir}",hashlib.sha256(request.encode('UTF-8')).hexdigest())
        #return f"{self.absolute_dir}/{hashlib.sha256(request.encode('UTF-8')).hexdigest()}"


    def get_entry(self,request):
        '''
        load cached response
        note this should only be used in a context where you trust the integrity of the cache files
        due to using pickle
        note also: no explicit handling of cache misses yet implemented
        '''

        with open(self.get_path(request),"rb") as f:
            return pickle.load(f)
        

    def set_entry(self,request,response):
        '''
        save a response to the cache
        '''

        with open(self.get_path(request),"wb") as fout:
            pickle.dump(response,fout)

    def do_request(self,request):
        '''
        automatically handle the cache operations for the call_back function
        '''

        if self.mode == "reuse" or (self.mode == "auto" and os.path.isfile(self.get_path(request))):
            return self.get_entry(request)

        response = requests.get(request)
        response.raise_for_status()

        if self.mode == "store" or self.mode == "auto": self.set_entry(request,response)
        return response

class MarkdownTable:
    '''
    helper class to accumulate rows of data with a header and optional summary row
    to be written to file as a markdown table
    '''
    def __init__(self,labels:str,keys:str,splitter='|',PASS="pass",FAIL="FAIL",NA="NA"):
        'specify column headers and variable names'
        self.labels = [x.strip() for x in labels.split(splitter)]
        self.keys = [x.strip() for x in keys.split(splitter)]
        assert len(self.keys) == len(self.labels)
        self.data = {key:[] for key in self.keys}
        self.summary = None
        self.PASS = PASS
        self.FAIL = FAIL
        self.NA = NA

    def __getitem__(self,key):
        'get last row of named column'
        assert key in self.keys
        assert len(self.data[key]) > 0
        return self.data[key][-1]

    def __setitem__(self,key,value):
        'set (ie overwrite) last row of named column'
        assert key in self.keys
        assert len(self.data[key]) > 0
        self.data[key][-1] = value

    def new_row(self,vars={}):
        'ingest the next row from a variables dict (eg locals())'
        for key in self.keys:
            if not key in vars:
                self.data[key].append(self.NA)
            else:
                self.data[key].append(vars[key])

    def update_row(self,vars):
        'update the last row from a variables dict (eg locals())'
        for key in self.keys:
            if not key in vars:
                self.data[key][-1] = self.NA
            else:
                self.data[key][-1] = vars[key]

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

    def regex_summary(self,key,patterns,format='{summary}',func=None):
        '''
        count how many cells match each pattern
        transform cell contents with optional callback function
        '''
        counts = defaultdict(int)

        for i,cell in enumerate(self.data[key]):
            if type(cell) == list:
                value = str(cell[0])
            else:
                value = str(cell)

            match=None
            for regex,tag in patterns.items():
                if re.search(regex,value):
                    match = tag
                    break
            if not match: match = "other"
            counts[match] += 1

            if func: self.data[key][i] = func(key,self.data[key][i],match)

        summary = ' '.join([f'n_{tag}={counts[tag]}' for tag in counts])
        self.add_summary(key,format.format(summary=summary))

    def make_fold(self,summary,details,quote=False):
        'make foldable/hideable html cell'
        if quote:
            format = "<details><summary>{summary}</summary>```{details}```</details>"
        else:
            format = "<details><summary>{summary}</summary>{details}</details>"

        return format.format(summary=summary,details=details)

    def generate_summary(self,counts):
        'generate the summary cell contents'

        total = sum([counts[tag] for tag in counts])
        summary = []
        fails = total

        if self.PASS in counts:
            summary.append(f'pass={counts[self.PASS]}')
            fails -= counts[self.PASS]
            del counts[self.PASS]
        if self.NA in counts:
            summary.append(f'NA={counts[self.NA]}')
            fails -= counts[self.NA]
            del counts[self.NA]

        if len(counts) > 1:
            # more than one error category, make folded details
            summary.append(f'FAIL={fails}') #summary has total fails
            summary = ' '.join(summary)
            details = ' '.join([f'n_{tag}={counts[tag]}' for tag in counts]) #give failures breakdown

            final = self.make_fold(summary,details) 
        else:
            # only one error category at most, use only a summary
            if len(counts) == 1:
                tag = list(counts)[0]
                summary.append(f'{tag}={counts[tag]}')

            final = summary = ' '.join(summary)
        
        return final

    def simple_summary(self,key):
        'count how many cells contain each distinct value'
        counts = defaultdict(int)   
        for cell in self.data[key]:
            if type(cell) == list:
                tag = str(cell[0])
            else:
                tag = str(cell)

            counts[tag] += 1

        self.add_summary(key,self.generate_summary(counts))

    def format_cell(self,cell):
        '''
        produce the final fully formatted markdown table cell contents
        '''

        if type(cell) == list:
            assert len(cell) == 2
            details = safe_md_string(cell[1])
            return self.make_fold(cell[0],details)
            
        return str(cell)

    def transform_column(self,key,func=None):
        'pass all column values through a function'
        for i in range(len(self.data[key])):
            if func:
                self.data[key][i] = func(self.data[key][i])
            else:
                self.data[key][i] = self.format_cell(self.data[key][i])

    def print_last_row(self):
        if self.n_rows() == 0:
            print('-')
            return
        print(' '.join([str(self.data[key][-1]) for key in self.data]))

    def print_col_lengths(self):
        print(' '.join([str(len(self.data[key])) for key in self.data]))

    def write(self,fout,sep='|',end='\n'):
        'write the markdown table to file'
        fout.write(sep + sep.join(self.labels) + sep + end)
        fout.write(sep + sep.join(['---' for x in self.labels]) + sep + end)
        if self.summary:
            fout.write(sep + sep.join([ str(self.summary[key]) for key in self.keys ]) + sep + end)

        for i in range(self.n_rows()):
            fout.write(sep + sep.join([ str(self.data[key][i]) for key in self.keys ])  + sep + end)

    def process_engine_outcomes(self,engine,key):
        '''
        process a column containing engine test outcomes/error messages
        categorise errors and generate summary counts
        '''

        #dict to record frequency of each engine error type
        errors = {'other':0}
        for pattern,error_tag in error_categories[engine].items():
            errors[error_tag] = 0

        for i in range(len(self.data[key])):
            if not self.data[key][i]:
                self.data[key][i] = 'pass'
                continue

            #make sure the error message will not break the markdown table
            error_str = safe_md_string(self.data[key][i])

            #category match the error message
            cell_text = None
            for pattern in error_categories[engine]:
                if re.search(pattern,error_str):
                    error_tag = error_categories[engine][pattern]
                    errors[error_tag] += 1
                    cell_text = self.make_fold(f"FAIL ({error_tag})",error_str,quote=True)
                    break
            
            if not cell_text:
                errors["other"] += 1
                cell_text = self.make_fold(f"FAIL (other)",error_str,quote=True)
            
            self.data[key][i] = cell_text

        #generate summary counts by error category
        total_errors = sum([ count for _,count in errors.items() ])
        details = ' '.join([ f'{error_tag}={count}' for error_tag,count in errors.items() ])
        summary_text = self.make_fold(f"fails={total_errors}",details)
        self.add_summary(key,summary_text)


def safe_md_string(value):
    '''
    make a string safe to insert into markdown table
    '''

    return str(value).replace("\n"," ").replace("\r","").replace("\t"," ").replace("   "," ").replace("  "," ")

import time

def download_file_from_link(engine, download_link, output_file='results.zip', max_wait_time=120, wait_time=2):
    """
    Function to download a file from a given URL.

    Parameters:
    download_link (str): The URL of the file to download.
    output_file (str): The name of the file to save the download as. Defaults to 'results.zip'.
    max_wait_time (int): The maximum time to wait for the file to be ready to download. Defaults to 120 seconds.
    wait_time (int): The time to wait between checks if the file is ready to download. Defaults to 2 seconds.

    Returns:
    bool: True if the file was downloaded successfully, False otherwise.
    """

    start_time = time.time()

    while True:
        # Check status of download_link
        response = requests.get(download_link)

        # If status is not 404 or max_wait_time has passed, break the loop
        if response.status_code != 404 or time.time() - start_time > max_wait_time:
            break

        # Wait for wait_time seconds before checking again
        time.sleep(wait_time)

    # If status == 200 then download the results
    if response.status_code == 200:
        print(f'Downloading {engine} results...')
        with requests.get(download_link, stream=True) as r:
            with open(output_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        # filepath where the file is downloaded
        filepath = os.path.abspath(output_file)
        return filepath
    else:
        print(f'Failed to download {engine} results.')
        raise HTTPError(f'Failed to download {engine} results.') 

# unzip the file in file_path if it is a zip file and remove the zip file, replace with the unzipped folder
def unzip_file(file_path, output_dir=None):
    """
    Unzip a file if it is a zip file.

    Parameters:
    file_path (str): The path to the file to unzip.
    output_dir (str): The directory to extract the contents of the zip file to. Defaults to None.

    Returns:
    str: The path to the unzipped folder.
    """

    # If the file is a zip file, unzip it
    if zipfile.is_zipfile(file_path):
        # If the output directory is not specified, use the directory of the file
        if output_dir is None:
            output_dir = os.path.dirname(file_path)

        # Create a ZipFile object
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Extract the contents of the zip file
            zip_ref.extractall(output_dir)

        # Remove the zip file
        os.remove(file_path)

        # Get the name of the unzipped folder
        unzipped_folder = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0])

        return unzipped_folder

    return file_path

def create_results_table(results, sbml_filepath, sedml_filepath, output_dir):
    """
    Create a markdown table of the results.
    
    Input: results, TYPES, sbml_filepath, sedml_filepath, ENGINES, output_dir
    Output: results_md_table

    """
    
    pass_html = "&#9989; PASS"
    fail_html = "&#10060; FAIL"
    warning_html = "&#9888; WARNING"
    xfail_html = "N/A"

    # Create a table of the results
    results_table = pd.DataFrame.from_dict(results).T
    # if list is three elements 
    if results_table.shape[1] == 3:
        results_table.columns = [PASS_FAIL, ERROR, TYPE]
    elif results_table.shape[1] == 2:
        results_table.columns = [PASS_FAIL, ERROR]

    results_table.index.name =  ENGINE
    results_table.reset_index(inplace=True)

    # Error
    results_table[ERROR] = results_table.apply(lambda x: None if x[PASS_FAIL] == x[ERROR] else x[ERROR], axis=1)
    results_table[PASS_FAIL] = results_table[PASS_FAIL].replace('other', 'FAIL')
    
    results_table[ERROR] = results_table[ERROR].apply(lambda x: ansi_to_html(x))
    results_table[ERROR] = results_table[ERROR].apply(lambda x: collapsible_content(x))

    results_table[PASS_FAIL] = results_table[PASS_FAIL].apply(lambda x: f'{fail_html}' if x == 'FAIL' \
                                                                        else f'{pass_html}' if x == 'pass' else x)
                                                          
    # d1 plot clickable link
    results_table[D1] = results_table[ENGINE].apply(lambda x: d1_plots_dict(output_dir).get(x, None))
    results_table[D1] = results_table[D1].apply(lambda x: create_hyperlink(x,title='plot'))

    if TYPE in results_table.columns:
        results_table[TYPE] = results_table[TYPE].apply(lambda x: collapsible_content(x,"".join(re.findall(r'[A-Z]', x))))

    for e in ENGINES.keys():
        compatibility_content = check_file_compatibility_test(e, sbml_filepath, sedml_filepath)

        print(e, compatibility_content[0] )
        if compatibility_content[0] == 'pass':
            results_table.loc[results_table[ENGINE] == e, COMPAT] = collapsible_content(compatibility_content[1], title=f'{pass_html}')
        elif compatibility_content[0] == 'unsure':
            results_table.loc[results_table[ENGINE] == e, COMPAT] = collapsible_content(compatibility_content[1], title=f'{warning_html}')
        else:
            results_table.loc[results_table[ENGINE] == e, COMPAT] = collapsible_content(compatibility_content[1], title=f'{fail_html}')

    # add xfail to engines that do not support sbml
    sbml_incompatible_ENGINES = [e for e in ENGINES.keys() if 'sbml' not in ENGINES[e]['formats'][0]]
    for e in sbml_incompatible_ENGINES:
        compatibility_content = check_file_compatibility_test(e, sbml_filepath, sedml_filepath)
        results_table.loc[results_table[ENGINE] == e, COMPAT] = collapsible_content(compatibility_content[1], title=f'{xfail_html}')
        results_table.loc[results_table[ENGINE] == e, PASS_FAIL] = f'{xfail_html}' 
           
        
    # add status message defined in ENGINES
    results_table[ENGINE] = results_table[ENGINE].apply(lambda x:  collapsible_content(f'{ENGINES[x]["url"]}<br>{ENGINES[x]["status"]}', x))

    return results_table


def run_biosimulators_remotely(sedml_file_name, 
                               sbml_file_name, 
                               d1_plots_remote_dir,  
                               test_folder='tests'):
    
    """ run with directory pointing towards the location of the sedml and sbml files"""
    
    remote_output_dir = 'remote_results'
    remote_output_dir = os.path.join(test_folder, remote_output_dir)

    download_links_dict = dict()
    for e in ENGINES.keys():
        download_link = run_biosimulators_remote(e, sedml_file_name, sbml_file_name)
        download_links_dict[e] = download_link

    extract_dir_dict = dict()
    results_remote = dict()
    for e, link in download_links_dict.items():
        try:
            extract_dir = get_remote_results(e, link, remote_output_dir)
        except HTTPError as emessage:
            results_remote[e] = ["FAIL", str(emessage), type(emessage).__name__]
            continue
        extract_dir_dict[e] = extract_dir

    for e, extract_dir in extract_dir_dict.items():
        status = ""
        error_message = ""
        exception_type = ""

        log_yml_path = find_file_in_dir('log.yml', extract_dir)[0]
        if not log_yml_path:
            status = None
            error_message = 'log.yml not found'
            continue
        with open(log_yml_path) as f:
            log_yml_dict = yaml.safe_load(f)
            if log_yml_dict['status'] == 'SUCCEEDED':
                status = 'pass'
            elif log_yml_dict['status'] == 'FAILED':
                status = 'FAIL'
                exception = log_yml_dict['exception']
                error_message = exception['message']
                exception_type = exception['type'] 
            else:
                status = None
            results_remote[e] = [status, error_message, exception_type] 

    file_paths = find_files(remote_output_dir, '.pdf')
    move_d1_files(file_paths, d1_plots_remote_dir)

    # remove the remote results directory
    if os.path.exists(remote_output_dir):
        shutil.rmtree(remote_output_dir)
        print('Removed ' + remote_output_dir + ' folder')

    return results_remote

def run_biosimulators_locally(sedml_file_name, 
                              sbml_file_name, 
                              d1_plots_local_dir, 
                              test_folder='tests'):
    results_local = {}

    output_folder = 'local_results'
    local_output_dir = os.path.join(test_folder, output_folder)

    for e in ENGINES.keys():
        print('Running ' + e)
        local_output_dir_e = os.path.abspath(os.path.join(local_output_dir, e))
        print(local_output_dir_e)
        record = run_biosimulators_docker(e, sedml_file_name, sbml_file_name, output_dir=local_output_dir_e)
        results_local[e] = record

    file_paths = find_files(local_output_dir, '.pdf')
    print('file paths:', file_paths)
    move_d1_files(file_paths, d1_plots_local_dir)

    # if it exists remove the output folder
    if os.path.exists(local_output_dir):
        shutil.rmtree(local_output_dir)
        print('Removed ' + local_output_dir + ' folder')

    return results_local



def create_combined_results_table(results_remote, 
                                  results_local, 
                                  sedml_file_name, 
                                  sbml_file_name, 
                                  d1_plots_local_dir, 
                                  d1_plots_remote_dir,
                                  test_folder='tests'):

    suffix_remote = ' (R)'
    suffix_local = ' (L)'
    
    # Create results tables for remote and local results
    results_table_remote = create_results_table(results_remote, sbml_file_name, sedml_file_name, d1_plots_remote_dir)
    results_table_local = create_results_table(results_local, sbml_file_name, sedml_file_name, d1_plots_local_dir)

    # Rename columns to distinguish between local and remote results except for Engine column
    results_table_remote.columns = [f"{col}{suffix_remote}" if col != ENGINE else col for col in results_table_remote.columns]
    results_table_local.columns = [f"{col}{suffix_local}" if col != ENGINE else col for col in results_table_local.columns]

    # Combine remote and local results
    combined_results = pd.merge(results_table_remote, results_table_local, on=ENGINE, how='outer')
    combined_results = combined_results.reindex(columns=[ENGINE] + sorted(combined_results.columns[1:]))
    combined_results[COMPAT] = combined_results[f"{COMPAT}{suffix_remote}"]
    combined_results.drop(columns=[f"{COMPAT}{suffix_remote}", f"{COMPAT}{suffix_local}"], inplace=True)

    # Define the order of columns
    cols_order = [
        ENGINE, 
        COMPAT, 
        f"{PASS_FAIL}{suffix_remote}", f"{PASS_FAIL}{suffix_local}", 
        f"{ERROR}{suffix_remote}", f"{ERROR}{suffix_local}", 
        f"{TYPE}{suffix_remote}",
        f"{D1}{suffix_remote}", f"{D1}{suffix_local}"
    ]

    combined_results = combined_results[cols_order]

    # Save the results to a Markdown file with utf-8 encoding
    path_to_results = os.path.join(test_folder, 'results_compatibility_biosimulators.md')
    print('Saving results to:', path_to_results)
    with open(path_to_results, 'w', encoding='utf-8') as f:
        f.write(combined_results.to_markdown())

    print('Number of columns in md table:', len(combined_results.columns))
    print('Number of rows in md table:', len(combined_results))
    print(combined_results.head())    

    return combined_results


def run_biosimulators_remotely_and_locally(sedml_file_name, 
                                 sbml_file_name,
                                 d1_plots_remote_dir, 
                                 d1_plots_local_dir,
                                 test_folder='tests'):
    
    results_remote = run_biosimulators_remotely(sedml_file_name=sedml_file_name, 
                                    sbml_file_name=sbml_file_name,
                                    d1_plots_remote_dir=d1_plots_remote_dir, 
                                    test_folder=test_folder)
    
    results_local = run_biosimulators_locally(sedml_file_name=sedml_file_name, 
                                    sbml_file_name=sbml_file_name,
                                    d1_plots_local_dir=d1_plots_local_dir, 
                                    test_folder=test_folder)

    results_table = create_combined_results_table(results_remote, 
                                    results_local, 
                                    sedml_file_name=sedml_file_name, 
                                    sbml_file_name=sbml_file_name,
                                    d1_plots_local_dir=d1_plots_local_dir,
                                    d1_plots_remote_dir=d1_plots_remote_dir, 
                                    test_folder=test_folder)
    
    return results_table