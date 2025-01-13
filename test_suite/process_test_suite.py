#!/usr/bin/env python3

"""
produce a markdown table of the results of running various tests on the SBML Test Suite

get this version of the test suite that includes sedml versions or the sedml validation will fail:
https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip
"""

import glob
import os
import sys
import warnings

import matplotlib
from pyneuroml.sbml import validate_sbml_files
from pyneuroml.sedml import validate_sedml_files

sys.path.append("..")
import utils

md_description = """
Markdown file description goes here.
"""


# suppress stdout output from validation functions to make progress counter readable
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
        "--cases",
        action="extend",
        nargs="+",
        type=str,
        default=[],
        help="Limit to the cases listed in the file. Empty list means no limit",
    )

    parser.add_argument(
        "--suite-path",
        action="store",
        type=str,
        default=".",
        help="Path to test suite directory, eg '~/repos/sbml-test-suite/cases/semantic'",
    )

    parser.add_argument(
        "--sbml-level_version",
        action="store",
        type=str,
        default="highest",
        help="SBML level and version to test (e.g. 'l3v2'), default is '' which will try to find the highest level and version in the folder",
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


def add_case_url(case, fpath, url_base):
    """
    insert URL link to original test case file online
    effectively replaces args.suite_path with args.suite_url_base
    this should produce a valid link for all the main intended use cases
    of testing the sbml test suite using the default args
    but will not handle all possible variations of globs and base directories
    in which case it should be disabled by setting --suite-url-base=''
    """

    url = os.path.join(url_base, fpath)
    new_item = f"[{case}]({url})"
    return new_item


def process_cases(args):
    """
    process the test cases and write results out as a markdown table
    with links to the test case files online (as noted above the sedml files are actually in a zip file)
    with a summary of how many cases were tested and how many tests failed
    """
    # set up the markdown table
    column_labels = (
        "case|valid-sbml|valid-sbml-units|valid-sedml|tellurium|xmlns-sbml-missing"
    )
    column_keys = "case|valid_sbml|valid_sbml_units|valid_sedml|tellurium_outcome|xmlns_sbml_missing"
    mtab = utils.MarkdownTable(column_labels, column_keys)

    # set the path to the test suite
    starting_dir = os.getcwd()  # where results will be written
    os.chdir(args.suite_path)  # change to test suite directory
    suite_path_abs = os.getcwd()  # absolute path to test suite

    # suppress interactive plots and load sup module to suppress stdout
    sup = utils.SuppressOutput(stdout=suppress_stdout)

    matplotlib.use("agg")
    # Suppress specific UserWarning caused by matplotlib (required to suppress interactive plots)
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        message="FigureCanvasAgg is non-interactive, and thus cannot be shown",
    )
    subfolders = (
        os.listdir(suite_path_abs)
        if args.limit == 0
        else os.listdir(suite_path_abs)[: args.limit]
    )

    for subfolder in subfolders:
        # if sbml_level_version is empty string (default), find the highest level and version in the folder
        if args.sbml_level_version == "highest":
            sedml_file_paths = glob.glob(os.path.join(subfolder, "*-sbml-*sedml.xml"))
            # get last entry in list of sedml_file_paths (because it has the highest level and version number considering the alphabetical order and naming convention)
            sedml_file_path = sedml_file_paths[-1] if sedml_file_paths != [] else []
            sbml_file_path = (
                sedml_file_path.replace("-sedml.xml", ".xml")
                if sedml_file_path != []
                else []
            )
        else:
            # find relevant files in the subfolder
            sbml_file_name = f"*-sbml-{args.sbml_level_version}.xml"
            sedml_file_name = f"*-sbml-{args.sbml_level_version}-sedml.xml"
            sbml_file_path = (
                glob.glob(os.path.join(subfolder, sbml_file_name))[0]
                if len(glob.glob(os.path.join(subfolder, sbml_file_name))) > 0
                else []
            )
            sedml_file_path = (
                glob.glob(os.path.join(subfolder, sedml_file_name))[0]
                if len(glob.glob(os.path.join(subfolder, sedml_file_name))) > 0
                else []
            )

        if sbml_file_path == [] or sedml_file_path == []:
            print(
                f"Folder {subfolder} has no SBML or SED-ML files {args.sbml_level_version}"
            )
            continue
        print(f"Processing {sbml_file_path} and {sedml_file_path}")

        # create table with results
        mtab.new_row()
        mtab["case"] = (
            add_case_url(sbml_file_path, sbml_file_path, args.suite_url_base)
            if args.suite_url_base != ""
            else sbml_file_path
        )

        # suppress stdout output from validation functions to make progress counter readable
        sup.suppress()
        mtab["valid_sbml"] = validate_sbml_files([sbml_file_path], strict_units=False)
        mtab["valid_sbml_units"] = validate_sbml_files(
            [sbml_file_path], strict_units=True
        )
        mtab["valid_sedml"] = validate_sedml_files([sedml_file_path])
        mtab["tellurium_outcome"] = utils.test_engine(
            "tellurium", sedml_file_path
        )  # run tellurium directly
        sup.restore()

        mtab["xmlns_sbml_missing"] = utils.xmlns_sbml_attribute_missing(sedml_file_path)
        matplotlib.pyplot.close("all")  # supresses error from building up plots

    # give failure counts
    for key in ["valid_sbml", "valid_sbml_units", "valid_sedml"]:
        mtab.add_count(key, lambda x: not x, "n_fail={count}")
        mtab.transform_column(key, lambda x: "pass" if x else "FAIL")

    # add counts for cases and missing xmlns_sbml attributes
    mtab.add_count("case", lambda _: True, "n={count}")
    mtab.add_count("xmlns_sbml_missing", lambda x: x, "n={count}")

    # process engine outcomes column(s)
    mtab.simple_summary("tellurium_outcome")
    mtab.transform_column("tellurium_outcome")

    # write out to file
    os.chdir(starting_dir)
    with open(args.output_file, "w") as fout:
        fout.write(md_description)
        mtab.write(fout)


if __name__ == "__main__":
    args = parse_arguments()

    process_cases(args)
