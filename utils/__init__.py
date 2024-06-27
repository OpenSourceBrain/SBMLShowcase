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

# 
engines = {
                        'amici': ('sbml', 'sedml'),\
                        'brian2': [('nml', 'sedml'),('lems', 'sedml'),('sbml', 'sedml')],\
                        'bionetgen': ('bngl', 'sedml'),\
                        'boolnet': ('sbmlqual', 'sedml'),\
                        'cbmpy': ('sbml', 'sedml'),\
                        'cobrapy': ('sbml', 'sedml'),\
                        'copasi': ('sbml', 'sedml'),\
                        'gillespy2': ('sbml', 'sedml'),\
                        'ginsim': ('sbmlqual', 'sedml'),\
                        'libsbmlsim': ('sbml', 'sedml'),\
                        'masspy': ('sbml', 'sedml'),\
                        'netpyne': ('sbml', 'sedml'),\
                        'neuron': [('nml', 'sedml'),('lems', 'sedml')],\
                        'opencor': ('sbml', 'sedml'),\
                        'pyneuroml': [('nml', 'sedml'),('lems', 'sedml')],\
                        'pysces': ('sbml', 'sedml'),\
                        'rbapy': ('rbapy', 'sedml'),\
                        'smoldyn':None ,\
                        'tellurium': ('sbml', 'sedml'),\
                        'vcell': None,\
                        'xpp': ('xpp', 'sedml')               
            }

types_dict = {
                'sbml':'SBML',\
                'sedml':'SED-ML',\
                'nml':'NeuroML',\
                'lems':'LEMS',\
                'sbmlqual':'SBML-qual',\
                'bngl':'BNGL',\
                'rbapy':'RBApy',\
                'xpp':'XPP',\
                'smoldyn':'Smoldyn'\
             }

error_categories = {
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

def move_d1_files(file_paths, plot_dir='d1_plots',engines=engines):
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir, exist_ok=True)

    for i in range(len(file_paths)):
        engine = [key for key in engines.keys() if key in file_paths[i]]
        new_file_name = '_'.join(engine) + '_' + os.path.basename(file_paths[i])
        new_file_path = os.path.join(plot_dir, new_file_name)
        print(new_file_path)
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        shutil.move(file_paths[i], new_file_path)

    return find_files(plot_dir, '.pdf')

def parse_error_message(text):
    if text != None:
        text_message = re.findall(r'"([^"]*)"', text) 
        if len(text_message) > 0:
            text = text_message
        else:
            text = text.replace('|', '')
            return text
        text = bytes(text[0], "utf-8").decode("unicode_escape")
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

def check_file_compatibility_test(engine, types_dict, model_filepath, experiment_filepath):
    '''
    Check if the file extensions suggest the file types are compatible with the engine
    '''
    input_filetypes = set(get_filetypes(model_filepath, experiment_filepath))
    input_file_types_text = [types_dict[i] for i in input_filetypes]


    engine_filetypes = engines[engine]
    if engine_filetypes is not None:
        # Flatten the list if the engine_filetypes is a list of tuples
        if all(isinstance(i, tuple) for i in engine_filetypes):
            engine_filetypes = {item for sublist in engine_filetypes for item in sublist}
        engine_file_types_text = [types_dict[i] for i in engine_filetypes if i in types_dict]
        if input_filetypes.issubset(engine_filetypes):
            return 'pass', (f"The file extensions suggest the input file types are '{input_file_types_text}'. These are compatible with {engine}")
        else:
            return 'FAIL', (f"The file extensions suggest the input file types are '{input_file_types_text}'. Tese are not compatible with {engine}. The following file types will be compatible {engine_file_types_text}")
    else:
        return 'FAIL', (f"{engine} compatible file types unknown.")


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


def run_biosimulators_docker(engine,sedml_filepath,sbml_filepath,output_dir=None,error_categories=error_categories):
    '''
    put the sedml and sbml file into an omex archive
    run it locally using a biosimulators docker
    categorise an error message in the log file
    '''

    #put the sedml and sbml into a combine archive
    omex_filepath = create_omex(sedml_filepath,sbml_filepath)

    try:
        biosimulators_core(engine,omex_filepath,output_dir=output_dir)
        return "pass" #no errors
    except Exception as e:
        #capture the error as a string which won't break markdown tables
        # error_str = safe_md_string(e)
        error_str = str(e)

    # #try to load the cleaner error message from the log.yml file
    # log_str = read_log_yml(os.path.join(os.path.dirname(omex_filepath),"log.yml"))

    # if log_str:
    #     error_str = safe_md_string(log_str)

    # #categorise the error string
    # for tag in error_categories:
    #     if re.search(error_categories[engine][tag],error_str):
    #         return [tag,f"```{error_str}```"]
    
    return ["other",f"```{error_str}```"]

def biosimulators_core(engine,omex_filepath,output_dir=None):
    '''
    run the omex file using biosimulators
    calls biosimulators via docker locally
    assumes local docker is setup
    engine can be any string that matches a biosimulators docker "URI":
    ghcr.io/biosimulators/{engine}
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
                        command=f"-i /root/in/{omex_file} -o /root/out")

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
