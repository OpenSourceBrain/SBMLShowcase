import shutil
import os
import pickle
import hashlib
import sys
from dataclasses import dataclass
from pyneuroml import tellurium
import re

#define error categories for detailed error counting per engine
# (currently only tellurium)
# key is regex match an error message, value is the tag/category used to report it
# see MarkdownTable.process_engine_outcomes
error_categories=\
{
    "tellurium":
        {
            "^Unable to support algebraic rules.":"algebraic",
            "^Unable to support delay differential equations.":"delay",
            "^Unknown ASTNode type of":"ASTNode",
            "^Mutable stochiometry for species which appear multiple times in a single reaction":"stochiometry",
            "^'float' object is not callable":"float",
            "is not a named SpeciesReference":"SpeciesRef",
            "reset":"reset",
            "^failed to validate SEDML file":"SEDMLfile",
            "^No sbml element exists":"noSBMLelement",
            "CV_ERR_FAILURE":"CV_ERR_FAILURE",
            "CV_TOO_MUCH_WORK":"CV_TOO_MUCH_WORK",
            "CV_CONV_FAILURE":"CV_CONV_FAILURE",
            "CV_ILL_INPUT":"CV_ILL_INPUT",
            "list index out of range":"outOfRange",
        },
}

def test_engine(engine,filename):
    '''
    test running the file with the given engine
    return the error generated, or None if no error was raised
    '''

    try:
        if engine == "tellurium":
            tellurium.run_from_sedml_file([filename],["-outputdir","none"])
            return None
        elif engine == "some_example_engine":
            #run it here
            return None
    except Exception as e:
        #return error object
        return e
        
    raise RuntimeError(f"unknown engine {engine}")

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
    '''

    def __init__(self,mode="off",direc="cache"):
        '''
        mode:
            "off" to disable caching (does not wipe any existing cache data)
            "store" to wipe and store fresh results in the cache
            "reuse" to reuse an existing cache
        direc: the directory used to store the cache
        '''
        self.mode = mode
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

        return f"{self.absolute_dir}/{hashlib.sha256(request.encode('UTF-8')).hexdigest()}"


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

    def do_request(self,call_back,request,*args,**kwargs):
        '''
        automatically handle the cache operations for the call_back function
        '''

        if self.mode == "reuse": return self.get_entry(request)

        response = call_back(request,*args,**kwargs)

        if self.mode == "store": self.set_entry(request,response)
        return response

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
                    cell_text=f"<details><summary>FAIL ({error_tag})</summary>```{error_str}```</details>"
                    break
            
            if not cell_text:
                errors["other"] += 1
                cell_text=f"<details><summary>FAIL (other)</summary>```{error_str}```</details>"
            
            self.data[key][i] = cell_text

        #generate summary counts by error category
        total_errors = sum([ count for _,count in errors.items() ])
        details = ' '.join([ f'{error_tag}={count}' for error_tag,count in errors.items() ])
        summary_text = f"<details><summary>fails={total_errors}</summary>{details}</details>"
        self.add_summary(key,summary_text)


def safe_md_string(error):
    '''
    make error string safe to insert into markdown table
    note: it will later be wrapped in triple backquotes after RE pattern matching
    '''

    return str(error).replace("\n"," ").replace("\r","").replace("\t"," ").replace("   "," ").replace("  "," ")
