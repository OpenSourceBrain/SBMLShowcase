#!/usr/bin/env python3

"""
produce a markdown table of the results of running various tests on the SBML Test Suite

get this version of the test suite that includes sedml versions or the sedml validation will fail:
https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip
"""

import os
import glob
from pyneuroml.sbml import validate_sbml_files
from pyneuroml.sedml import validate_sedml_files
from pyneuroml import tellurium
import matplotlib
from collections import defaultdict
import re

# define error categories for detailed error counting per engine
# (currently only tellurium)
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
        },
}


def parse_arguments():
    "Parse command line arguments"

    import argparse

    parser = argparse.ArgumentParser(
        description="Run various tests on the SBML Test Suite (or any similar set of SBML/SEDML files)"
    )

    parser.add_argument(
        "--limit",
        action="store",
        type=int,
        default=0,
        help="Limit to the first n test cases, 0 means no limit",
    )

    parser.add_argument(
        "--suite-path",
        action="store",
        type=str,
        default=".",
        help="Path to test suite directory, eg '~/repos/sbml-test-suite/cases/semantic'",
    )

    parser.add_argument(
        "--suite-glob",
        action="store",
        type=str,
        default="000*/*-sbml-l3v2.xml",
        help="Shell-style glob matching test suite file(s) within suite_path, eg '000*/*-sbml-l3v2.xml'",
    )

    parser.add_argument(
        "--suite-url-base",
        action="store",
        type=str,
        default="https://github.com/sbmlteam/sbml-test-suite/blob/release/cases/semantic",
        help="Base of the URL-to-suite-test-cases link to embed in results, use '' empty string to disable links",
    )

    parser.add_argument(
        "--output-file",
        action="store",
        type=str,
        default="results.md",
        help="Path to file results will be written to, any parent directories must exist, eg ./results.md",
    )

    return parser.parse_args()

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


def add_case_url(case,fpath,url_base):
    '''
    insert URL link to original test case file online
    effectively replaces args.suite_path with args.suite_url_base
    this should produce a valid link for all the main intended use cases
    of testing the sbml test suite using the default args
    but will not handle all possible variations of globs and base directories
    in which case it should be disabled by setting --suite-url-base=''
    '''

    url = os.path.join(url_base,fpath)
    new_item = f'[{case}]({url})'
    return new_item

def make_md_error_string(error):
    '''
    make error string safe to insert into markdown table
    note: it will later be wrapped in triple backquotes after RE pattern matching
    '''

    return str(error).replace("\n"," ").replace("\r","").replace("\t"," ").replace("   "," ").replace("  "," ")

def process_error(engine,error,engine_errors):
    'reduce error to a short identifier that can be displayed in the table'

    global okay,fail,error_categories

    error_str = make_md_error_string(error)

    cell_text = None
    for pattern in error_categories[engine]:
        if re.search(pattern,error_str):
            error_tag = error_categories[engine][pattern]
            engine_errors[engine][error_tag] += 1
            cell_text=f"<details><summary>{fail} ({error_tag})</summary>```{error_str}```</details>"
            break
    
    if not cell_text:
        engine_errors[engine]["other"] += 1
        cell_text=f"<details><summary>{fail} (other)</summary>```{error_str}```</details>"


    return cell_text

def test_engine(engine,filename,engine_errors=None):
    'test running the file with the given engine'

    global okay,fail

    try:
        if engine == "tellurium":
            tellurium.run_from_sedml_file([filename],["-outputdir","none"])
            return okay
        elif engine == "some_example_engine":
            #run it here
            return okay
    except Exception as e:
        if engine_errors != None:
            #return informative error identifier
            return process_error(engine,e,engine_errors)
        else:
            #return simple "FAIL" indicator
            return fail
        
    raise RuntimeError(f"unknown engine {engine}")


def insert_engine_error_summaries(summary,engine_errors):
    'insert engine error summary counts into table header line'

    for engine in engine_errors:
        total_errors = sum([ count for error_tag,count in engine_errors[engine].items() ])
        details = ' '.join([ f'{error_tag}={count}' for error_tag,count in engine_errors[engine].items() ])
        element = f"<details><summary>fails={total_errors}</summary>{details}</details>"
        summary = summary.replace('{'+engine+'_summary}',element)

    return summary

def process_cases(args):
    """
    process the test cases and write results out as a markdown table
    with links to the test case files online (as noted above the sedml files are actually in a zip file)
    with a summary of how many cases were tested and how many tests failed
    """

    global error_categories

    header = "|case|valid-sbml|valid-sbml-units|valid-sedml|tellurium|"
    sep = "|---|---|---|---|---|"
    summary="|cases={n_cases}|fails={n_failing[valid_sbml]}|fails={n_failing[valid_sbml_units]}|fails={n_failing[valid_sedml]}|{tellurium_summary}|"
    row = "|{case}|{valid_sbml}|{valid_sbml_units}|{valid_sedml}|{tellurium_outcome}|"

    #dict to record frequency of each engine error type
    engine_errors = {}

    #make sure engine errors is ready to receive error counts from all engines
    for engine in error_categories:
        engine_errors[engine] = {}
        engine_errors[engine]['other'] = 0
        for pattern,error_tag in error_categories[engine].items():
            engine_errors[engine][error_tag] = 0


    with open(args.output_file, "w") as fout:
        #accumulate output in memory so we can put the summary at the top instead of at the end
        output = []
        output.append(header)
        output.append(sep)
        output.append("<results summary goes here>")
        n_cases = 0
        n_failing = {"valid_sbml":0, "valid_sbml_units":0, "valid_sedml":0}


        os.chdir(args.suite_path)
        for fpath in sorted(glob.glob(args.suite_glob)):
            if args.limit and args.limit > 0 and n_cases >= args.limit: break
            n_cases +=1
            sedml_path = fpath.replace(".xml", "-sedml.xml")
            print(fpath)
            assert os.path.isfile(fpath)
            assert os.path.isfile(sedml_path)
            case = os.path.basename(fpath)
            if args.suite_url_base != '': case = add_case_url(case,fpath,args.suite_url_base)
            valid_sbml = pass_or_fail(validate_sbml_files([fpath], strict_units=False))
            valid_sbml_units = pass_or_fail(validate_sbml_files([fpath], strict_units=True))
            valid_sedml = pass_or_fail(validate_sedml_files([sedml_path]))
            tellurium_outcome = test_engine("tellurium",sedml_path,engine_errors) #note: used in row.format below via locals()
            output.append(row.format(**locals()))

            #tally results so we can provide a summary
            global okay,fail
            if valid_sbml != okay: n_failing["valid_sbml"] += 1
            if valid_sbml_units != okay: n_failing["valid_sbml_units"] += 1
            if valid_sedml != okay: n_failing["valid_sedml"] += 1

            #stop matplotlib plot from building up
            matplotlib.pyplot.close()

        #add detailed error statistics to engine column header summary cells
        summary = insert_engine_error_summaries(summary,engine_errors)

        #complete the header
        output[2] = summary.format(**locals())

        #write to output file
        for line in output: fout.write(line+'\n')


if __name__ == "__main__":
    args = parse_arguments()

    process_cases(args)
