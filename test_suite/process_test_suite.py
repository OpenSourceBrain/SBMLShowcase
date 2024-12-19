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
import pickle
import shutil
import yaml

import matplotlib
from pyneuroml.sbml import validate_sbml_files
from pyneuroml.sedml import validate_sedml_files

sys.path.append("..")
import utils

md_description = """
Markdown file description goes here.
"""

tmp_dir = "tmplocalfiles"

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

def get_test_suite_files_paths(suite_path_abs, sbml_level_version, limit=0):

    start_dir = os.getcwd()
    # get lists of sedml and sbml file paths in subfolders
    file_paths = {}

    subfolders = [
        f for f in os.listdir(suite_path_abs)
        if os.path.isdir(os.path.join(suite_path_abs, f)) and (limit == 0 or os.listdir(suite_path_abs).index(f) < limit)
    ]

    for subfolder in subfolders:
        dir_path = os.path.join(suite_path_abs, subfolder)
        os.chdir(dir_path)
        if sbml_level_version == "highest":
            sedml_file_paths = sorted(glob.glob("*-sbml-*sedml.xml"))
            highest_sedml_path = os.path.abspath(sedml_file_paths[-1]) if sedml_file_paths else ""
            highest_sbml_path = os.path.abspath(highest_sedml_path.replace("-sedml.xml", ".xml")) if highest_sedml_path else ""
        else:
            sbml_file_name = f"*-sbml-{sbml_level_version}.xml"
            sedml_file_name = f"*-sbml-{sbml_level_version}-sedml.xml"
            highest_sbml_path = os.path.abspath(glob.glob(sbml_file_name)[0]) if glob.glob(sbml_file_name) else ""
            highest_sedml_path = os.path.abspath(glob.glob(sedml_file_name)[0]) if glob.glob(sedml_file_name) else ""

        if not highest_sedml_path or not highest_sbml_path:
            print(f"Folder {subfolder} has no SBML or SED-ML files {sbml_level_version}")
            continue

        file_paths[subfolder] = {'sbml': highest_sbml_path, 'sedml': highest_sedml_path}

    os.chdir(start_dir)
    return file_paths


def load_pickle(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except (EOFError, pickle.UnpicklingError) as e:
            print(f"Error loading pickle file {file_path}: {e}")
            return {}
    return {}

def save_pickle(data, file_path):
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    except pickle.PicklingError as e:
        print(f"Error saving pickle file {file_path}: {e}")

def run_test_suite_batch_remotely(engine_keys, file_paths, limit=0, use_pickle=True):
    
    file_paths_items = list(file_paths.items())  # Convert dict_items to a list

    for subfolder, paths in (file_paths_items if limit == 0 else file_paths_items[:limit]):
        sbml_file_path = paths['sbml']
        sedml_file_path = paths['sedml']
        file_path_dir = os.path.dirname(sedml_file_path)
        os.chdir(file_path_dir)
        
        pickle_file_path = os.path.join(file_path_dir, f"{subfolder}_remote_links.p")
        
        # Load existing results from pickle file if it exists
        results_remote_links = load_pickle(pickle_file_path) if use_pickle else {}
        
        if subfolder in results_remote_links:
            print(f"Using pickled results for test suite example {subfolder}")
            results_remote_links[subfolder].update({"folder_dir": file_path_dir})
            # Save results to pickle file after each subfolder
            save_pickle(results_remote_links, pickle_file_path)
            continue

        

        for engine in engine_keys:
            try:
                results_remote = utils.run_biosimulators_remote(
                    engine, os.path.basename(sedml_file_path), os.path.basename(sbml_file_path)
                )
                results_remote_links[subfolder][engine] = results_remote
            except Exception as e:
                print(f"Error processing {subfolder} with engine {engine}: {e}")
                results_remote_links[subfolder][engine] = {"error": str(e)}
        
        # Save results to pickle file after each subfolder
        save_pickle(results_remote_links, pickle_file_path)
    return print("All test suite examples submitted or pickled")

def merge_pickled_links(file_paths, limit=0):
    file_paths_items = list(file_paths.items()) 
    merged_links = {}
    
    for subfolder, paths in (file_paths_items if limit == 0 else file_paths_items[:limit]):
        file_path_dir = os.path.dirname(paths['sedml'])
        pickle_file_path = os.path.join(file_path_dir, f"{subfolder}_remote_links.p")
        pickled_data = load_pickle(pickle_file_path)
        merged_links.update(pickled_data)
    
    return merged_links

def get_remote_results_from_links(links_dict):
    """Run with directory pointing towards the location of the sedml and sbml files"""
    extract_dir_dict = download_remote_test_suite_results(links_dict)
    results_remote = process_results(extract_dir_dict)
    # remove_output_folders(extract_dir_dict)
    return results_remote

def download_remote_test_suite_results(links_dict, refresh=False, limit=0):
    extract_dir_dict = {}
    for subfolder, links in (links_dict.items() if limit == 0 else list(links_dict.items())[:limit]):
        folder_dir = links["folder_dir"]
        links.pop("folder_dir")  # remove folder_dir key from links_dict
        subfolder_dict = {"folder_dir": folder_dir, "extract_dir": {}}
        print(f"Downloading results for {subfolder} in {folder_dir}")
        for engine, engine_links in links.items():
            if engine in utils.ENGINES.keys() and "download" in engine_links:
                os.chdir(folder_dir)
                folder = os.path.join("results_remote", engine)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                os.chdir(folder)
                files_in_folder = os.listdir()
                zip_in_folder = any([f.endswith(".zip") for f in files_in_folder])
                if not zip_in_folder or refresh:
                    extract_dir = utils.download_file_from_link(engine, engine_links["download"])
                    print(f"Downloaded {engine} results to {extract_dir}")
                else:
                    zip_path = [f for f in files_in_folder if f.endswith(".zip")][0]
                    extract_dir = os.path.join(folder_dir, folder, zip_path)
                
                subfolder_dict["extract_dir"][engine] = extract_dir

        extract_dir_dict[subfolder] = subfolder_dict

    return extract_dir_dict

import zipfile

def unzip_files():
    """ Unzip all zip files in the current directory """
    zip_files = [f for f in os.listdir() if f.endswith(".zip")]
    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall()


def process_results(extract_dir_dict):
    results_remote = {}
    for subfolder, extract_dirs in extract_dir_dict.items():
        results_remote[subfolder] = {}
        for engine, zip_file in extract_dirs["extract_dir"].items():
            output_folder = os.path.dirname(zip_file)
            os.chdir(output_folder)
            unzip_files()
            log_yml_files = utils.find_files(output_folder, "log.yml")
            if log_yml_files:
                log_yml_path = log_yml_files[0]
                with open(log_yml_path) as f:
                    log_yml_dict = yaml.safe_load(f)
            else:
                log_yml_dict = {}
            results_remote[subfolder][engine] = {"log_yml": log_yml_dict}

    return results_remote

def remove_output_folders(extract_dir_dict):
    for _, extract_dirs in extract_dir_dict.items():
        os.chdir(extract_dirs["folder_dir"])
        if os.path.exists("results_remote"):
            shutil.rmtree("results_remote")   
    return

def process_cases(args):
    """
    process the test cases and write results out as a markdown table
    with links to the test case files online (as noted above the sedml files are actually in a zip file)
    with a summary of how many cases were tested and how many tests failed
    """
    # set up the markdown table
    column_labels = (
        "case|valid-sbml|valid-sbml-units|valid-sedml|tellurium|xmlns-sbml-missing|tellurium-remote|copasi-remote"
    )
    column_keys = "case|valid_sbml|valid_sbml_units|valid_sedml|tellurium_outcome|xmlns_sbml_missing|tellurium_remote_outcome|copasi_remote_outcome"
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
        subfolder_dir = os.path.join(suite_path_abs, subfolder)
        os.chdir(subfolder_dir)
        pickle_name = f"{subfolder}_mtab.p"
        pickle_path = os.path.join(subfolder_dir, tmp_dir, subfolder, pickle_name)

        # if sbml_level_version is empty string (default), find the highest level and version in the folder
        if args.sbml_level_version == "highest":
            sedml_file_paths = glob.glob("*-sbml-*sedml.xml")
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
                glob.glob(sbml_file_name)[0]
                if len(glob.glob(sbml_file_name)) > 0
                else []
            )
            sedml_file_path = (
                glob.glob(sedml_file_name)[0]
                if len(glob.glob(subfolder, sedml_file_name)) > 0
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

        # COPASI and Tellurium remote tests
        engine_keys = ["copasi", "tellurium"]
        test_folder = "tests"
        d1_plots_remote_dir = os.path.join(test_folder, "d1_plots_remote")

        results_remote = utils.run_biosimulators_remotely(
            engine_keys,
            sedml_file_name=os.path.basename(sedml_file_path),
            sbml_file_name=os.path.basename(sbml_file_path),
            d1_plots_remote_dir=d1_plots_remote_dir,
            test_folder=test_folder,
        )

        for e in engine_keys:
            # only if log_yml key is present
            if "log_yml" in results_remote[e]:
                results_remote_processed = utils.process_log_yml_dict(
                    results_remote[e]["log_yml"]
                )
            else:
                results_remote_processed = {
                    "status": "ERROR",
                    "error_message": "log_yml key not found",
                    "exception_type": "KeyError",
                }
            mtab_remote_outcome_key = f"{e}_remote_outcome"

            info_submission = f"Download: {results_remote[e]['download']}<br><br>Logs: {results_remote[e]['logs']}<br><br>View: {results_remote[e]['view']}<br><br>HTTP response: {str(results_remote[e]['response'])}"
            error_message_string = f'Error message: {results_remote_processed["error_message"]}<br><br>Exception type: {results_remote_processed["exception_type"]}'

            if results_remote_processed["error_message"] != "":
                info_submission = info_submission + f"<br><br>{error_message_string}"

            mtab[mtab_remote_outcome_key] = [
                results_remote_processed["status"],
                info_submission,
            ]

        matplotlib.pyplot.close("all")  # supresses error from building up plots
        mtab_dict = {"mtab_row": mtab, "results_remote": results_remote}
        pickle.dump(mtab_dict, open(pickle_name, "wb"))

    # give failure counts
    for key in ["valid_sbml", "valid_sbml_units", "valid_sedml"]:
        mtab.add_count(key, lambda x: x is False, "n_fail={count}")
        mtab.transform_column(key, lambda x: "pass" if x else "FAIL")

    # add counts for cases and missing xmlns_sbml attributes
    mtab.add_count("case", lambda _: True, "n={count}")
    mtab.add_count("xmlns_sbml_missing", lambda x: x is True, "n={count}")

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

    suite_path = r"C:\Users\prins\GitHub\SBMLShowcase\test_suite\SBML_test_suite\semantic"
    args.suite_path = suite_path

    file_paths = get_test_suite_files_paths(args.suite_path, args.sbml_level_version, limit=0)
    run_test_suite_batch_remotely(["copasi", "tellurium"], file_paths, limit=0)
    remote_links = merge_pickled_links(file_paths, limit=0)
    results_remote = get_remote_results_from_links(remote_links)
    # save results remote as pickle file in directory in which the current file lives
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    save_pickle(results_remote, "results_remote.p")

    print(remote_links)

    # process_cases(args)
