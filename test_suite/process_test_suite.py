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
import matplotlib
import sys
import warnings

sys.path.append("..")
import utils

md_description = \
'''
Markdown file description goes here.
'''


#suppress stdout output from validation functions to make progress counter readable
suppress_stdout = True

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



def process_cases(args):
    """
    process the test cases and write results out as a markdown table
    with links to the test case files online (as noted above the sedml files are actually in a zip file)
    with a summary of how many cases were tested and how many tests failed
    """

    #allow stdout/stderr from validation tests to be suppressed to improve progress count readability
    sup = utils.SuppressOutput(stdout=suppress_stdout)

    column_labels = "case|valid-sbml|valid-sbml-units|valid-sedml|tellurium"
    column_keys  =  "case|valid_sbml|valid_sbml_units|valid_sedml|tellurium_outcome"
    mtab = utils.MarkdownTable(column_labels,column_keys)

    #open file now to make sure output path is with respect to initial working directory
    #not the test suite folder
    starting_dir = os.getcwd()

    n_cases = 0

    os.chdir(args.suite_path)
    suite_path_abs = os.getcwd()
    sbml_list = sorted(glob.glob(args.suite_glob))

    for sbml_path in sbml_list:
        if args.limit and args.limit > 0 and n_cases >= args.limit: break
        matplotlib.use("agg")
        warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive, and thus cannot be shown")

        mtab.new_row()
        n_cases +=1

        case_dir = os.path.dirname(sbml_path)
        os.chdir(suite_path_abs)
        os.chdir(case_dir)

        sbml_file = os.path.basename(sbml_path)
        sedml_file = sbml_file.replace(".xml", "-sedml.xml")

        print(f"{n_cases}/{len(sbml_list)} {sbml_file}")
        assert os.path.isfile(sbml_file)
        assert os.path.isfile(sedml_file)
        case = sbml_file
        if args.suite_url_base != '': case = add_case_url(case,sbml_path,args.suite_url_base)
        mtab['case'] = case

        sup.suppress() #suppress printing warnings to stdout
        mtab['valid_sbml'] = validate_sbml_files([sbml_file], strict_units=False)
        mtab['valid_sbml_units'] = validate_sbml_files([sbml_file], strict_units=True)
        mtab['valid_sedml'] = validate_sedml_files([sedml_file])
        mtab['tellurium_outcome'] = utils.test_engine("tellurium",sedml_file) # run tellurium directly
        sup.restore()

        #stop matplotlib plots from building up
        matplotlib.pyplot.close() # TODO: test on MAC whether this is still necessary after switching to Agg
        # switch agg off
        matplotlib.use("TkAgg")

    #give failure counts
    for key in ['valid_sbml','valid_sbml_units','valid_sedml']:
        mtab.add_count(key,lambda x:x==False,'n_fail={count}')
        mtab.transform_column(key,lambda x:'pass' if x else 'FAIL')

    #process engine outcomes column(s)
    mtab.simple_summary('tellurium_outcome')
    mtab.transform_column('tellurium_outcome')
        
    #write out to file
    os.chdir(starting_dir)
    with open(args.output_file, "w") as fout:
        fout.write(md_description)
        mtab.write(fout)
        

if __name__ == "__main__":
    args = parse_arguments()

    process_cases(args)
