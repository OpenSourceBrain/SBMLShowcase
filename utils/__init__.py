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
