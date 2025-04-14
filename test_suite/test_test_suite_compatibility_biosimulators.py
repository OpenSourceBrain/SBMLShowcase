#!/usr/bin/env python3

"""
produce a markdown table of the results of running various tests on the SBML Test Suite

get this version of the test suite that includes sedml versions or the sedml validation will fail:
https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip
"""

import glob
import os
import shutil
import sys

sys.path.append("..")
import utils

engines = utils.ENGINES


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
        "--suite_path",
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

    return parser.parse_args()


def process_cases(args):
    """
    process the test cases and write results out as a markdown table
    with links to the test case files online (as noted above the sedml files are actually in a zip file)
    with a summary of how many cases were tested and how many tests failed

    examples of command line instructions

    To test all the cases in the test suite:
    python test_test_suite_compatibility_biosimulators.py --limit 0 --suite-path /path/to/sbml-test-suite/cases/semantic --sbml-level_version l3v2

    To test the first 10 cases in the test suite:
    python test_test_suite_compatibility_biosimulators.py --limit 10 --suite-path /path/to/sbml-test-suite/cases/semantic --sbml-level_version l3v2

    To test the highest level and version of SBML of the first 5 cases in the test suite:
    python test_test_suite_compatibility_biosimulators.py --limit 5 --suite-path /path/to/sbml-test-suite/cases/semantic --sbml-level_version highest

    To test cases 00001 and 01186 in the test suite:
    python test_test_suite_compatibility_biosimulators.py --cases 00001 01186 --suite-path /path/to/sbml-test-suite/cases/semantic --sbml-level_version highest
    """

    starting_dir = os.getcwd()  # where results will be written

    os.chdir(args.suite_path)  # change to test suite directory
    suite_path_abs = os.getcwd()  # absolute path to test suite

    if args.cases != []:
        subfolders = args.cases
    else:
        subfolders = (
            os.listdir(suite_path_abs)
            if args.limit == 0
            else os.listdir(suite_path_abs)[: args.limit]
        )

    print(f"Processing {len(subfolders)} subfolders in {args.suite_path}")
    test_folder = "tests"

    for subfolder in subfolders:
        # create an equivalently named folder in the starting directory
        os.chdir(args.suite_path)
        print(f"Processing {subfolder}")

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

        new_subfolder = "test_" + subfolder
        new_directory = os.path.join(starting_dir, new_subfolder)
        os.makedirs(new_directory, exist_ok=True)
        print(
            f"Copying {sbml_file_path} and {sedml_file_path} to {starting_dir}/{subfolder}"
        )
        new_sbml_file_path = os.path.join(
            new_directory, os.path.basename(sbml_file_path)
        )
        new_sedml_file_path = os.path.join(
            new_directory, os.path.basename(sedml_file_path)
        )
        shutil.copy(sbml_file_path, new_sbml_file_path)
        shutil.copy(sedml_file_path, new_sedml_file_path)

        os.chdir(new_directory)
        print(f"Changed to {new_directory}")

        engine_list = list(engines.keys())
        # engine_list = engine_list[:5]

        utils.run_biosimulators_remotely_and_locally(
            engine_list,
            os.path.basename(sedml_file_path),
            os.path.basename(sbml_file_path),
            os.path.join(test_folder, "d1_plots_remote"),
            os.path.join(test_folder, "d1_plots_local"),
            test_folder=test_folder,
        )


if __name__ == "__main__":
    args = parse_arguments()
    if len(sys.argv) == 1:
        # No command line arguments provided, set default values
        args.cases = ["00001", "01186"]
        args.sbml_level_version = "highest"
    args.suite_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "SBML_test_suite", "semantic"
    )
    process_cases(args)
