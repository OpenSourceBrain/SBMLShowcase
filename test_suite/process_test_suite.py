#!/usr/bin/env python3

"""
produce a markdown table of the results of running various tests on the SBML Test Suite

get this version of the test suite that includes sedml versions or the sedml validation will fail:
https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip
"""

import glob
import os
import pickle
import shutil
import sys
import time
import warnings
import zipfile

import matplotlib
import requests
import yaml
from pyneuroml.sbml import validate_sbml_files
from pyneuroml.sedml import validate_sedml_files

sys.path.append("..")
import utils

md_description = """
SBML Test Suite validation and simulation results using Tellurium installed natively and Tellurium and COPASI run remotely through BioSimulators.
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
        help="Limit to the cases listed. No specific cases will be tested when an empty list is provided.",
    )

    parser.add_argument(
        "--skip",
        action="extend",
        nargs="+",
        type=str,
        default=[],
        help="Skip cases listed.",
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


def get_test_suite_files_paths(suite_path_abs, sbml_level_version, subfolders):
    start_dir = os.getcwd()
    # get lists of sedml and sbml file paths in subfolders
    file_paths = {}

    for subfolder in subfolders:
        dir_path = os.path.join(suite_path_abs, subfolder)
        os.chdir(dir_path)
        if sbml_level_version == "highest":
            sedml_file_paths = sorted(glob.glob("*-sbml-*sedml.xml"))
            highest_sedml_path = (
                os.path.abspath(sedml_file_paths[-1]) if sedml_file_paths else ""
            )
            highest_sbml_path = (
                os.path.abspath(highest_sedml_path.replace("-sedml.xml", ".xml"))
                if highest_sedml_path
                else ""
            )
        else:
            sbml_file_name = f"*-sbml-{sbml_level_version}.xml"
            sedml_file_name = f"*-sbml-{sbml_level_version}-sedml.xml"
            highest_sbml_path = (
                os.path.abspath(glob.glob(sbml_file_name)[0])
                if glob.glob(sbml_file_name)
                else ""
            )
            highest_sedml_path = (
                os.path.abspath(glob.glob(sedml_file_name)[0])
                if glob.glob(sedml_file_name)
                else ""
            )

        if not highest_sedml_path or not highest_sbml_path:
            print(
                f"Folder {subfolder} has no SBML or SED-ML files {sbml_level_version}"
            )
            continue

        file_paths[subfolder] = {"sbml": highest_sbml_path, "sedml": highest_sedml_path}

    os.chdir(start_dir)
    return file_paths


def load_pickle(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading pickle file {file_path}: {e}")
            return {}
    return {}


def save_pickle(data, file_path):
    try:
        with open(file_path, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Error saving pickle file {file_path}: {e}")


def run_test_suite_batch_remotely(engine_keys, file_paths, limit=0, use_pickle=True):
    file_paths_items = list(file_paths.items())  # Convert dict_items to a list
    results_remote_links = {}  # Initialize results_remote_links

    for subfolder, paths in (
        file_paths_items if limit == 0 else file_paths_items[:limit]
    ):
        sbml_file_path = paths["sbml"]
        sedml_file_path = paths["sedml"]
        file_path_dir = os.path.dirname(sedml_file_path)
        os.chdir(file_path_dir)

        pickle_file_path = os.path.join(file_path_dir, f"{subfolder}_remote_links.p")
        results_remote_links = {subfolder: {"folder_dir": file_path_dir}}

        if use_pickle:
            if os.path.exists(pickle_file_path):
                print(f"Pickled links found for test suite example {subfolder}")
                continue
            else:
                print(f"No pickled links found for test suite example {subfolder}")

        new_results_remote_links = {}
        for engine in engine_keys:
            try:
                results_remote = utils.run_biosimulators_remote(
                    engine,
                    os.path.basename(sedml_file_path),
                    os.path.basename(sbml_file_path),
                )
                new_results_remote_links[engine] = results_remote
            except Exception as e:
                print(f"Error processing {subfolder} with engine {engine}: {e}")
                new_results_remote_links[engine] = {"error": str(e)}

        results_remote_links[subfolder].update(new_results_remote_links)
        save_pickle(results_remote_links, pickle_file_path)
        print("All test suite examples submitted for remote testing.")
    return


def merge_pickled_links(file_paths, limit=0):
    file_paths_items = list(file_paths.items())
    merged_links = {}

    for subfolder, paths in (
        file_paths_items if limit == 0 else file_paths_items[:limit]
    ):
        file_path_dir = os.path.dirname(paths["sedml"])
        pickle_file_path = os.path.join(file_path_dir, f"{subfolder}_remote_links.p")
        pickled_data = load_pickle(pickle_file_path)
        merged_links.update(pickled_data)

    return merged_links


def get_remote_results_from_links(links_dict):
    """Run with directory pointing towards the location of the sedml and sbml files"""
    extract_dir_dict = download_remote_test_suite_results(links_dict)
    log_yml_dict = create_log_yml_dict(extract_dir_dict)
    # remove_output_folders(extract_dir_dict)
    return log_yml_dict


def download_remote_test_suite_results(links_dict, refresh=False, limit=0):
    """
    If refresh is True, download results even if a zip file is already present in the folder.
    limit is the number of subfolders to process, 0 means no limit.
    """
    extract_dir_dict = {}
    for subfolder, links in (
        links_dict.items() if limit == 0 else list(links_dict.items())[:limit]
    ):
        folder_dir = links["folder_dir"]
        links.pop("folder_dir")  # remove folder_dir key from links_dict
        subfolder_dict = {"folder_dir": folder_dir, "extract_dir": {}}

        for engine, engine_links in links.items():
            if engine in utils.ENGINES.keys() and "download" in engine_links:
                os.chdir(folder_dir)
                folder = os.path.join("results_remote", engine)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                os.chdir(folder)
                zip_in_folder = any([f.endswith(".zip") for f in os.listdir()])
                if not zip_in_folder or refresh:
                    extract_dir = utils.download_file_from_link(
                        engine, engine_links["download"]
                    )
                    print(f"Downloaded {engine} results to {extract_dir}")
                else:
                    zip_path = [f for f in os.listdir() if f.endswith(".zip")][0]
                    extract_dir = os.path.join(folder_dir, folder, zip_path)

                subfolder_dict["extract_dir"][engine] = extract_dir

        extract_dir_dict[subfolder] = subfolder_dict

    return extract_dir_dict


def unzip_files(file_paths=[]):
    """Unzip all zip files in the current directory if no file paths are provided"""
    if file_paths != []:
        zip_files = file_paths
    zip_files = [f for f in os.listdir() if f.endswith(".zip")]
    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall()


def create_log_yml_dict(extract_dir_dict):
    log_yml_dict = {}
    for subfolder, extract_dirs in extract_dir_dict.items():
        log_yml_dict[subfolder] = {}
        for engine, zip_file in extract_dirs["extract_dir"].items():
            output_folder = os.path.dirname(zip_file)
            os.chdir(output_folder)
            unzip_files()
            log_yml_files = utils.find_files(output_folder, "log.yml")
            if log_yml_files:
                log_yml_path = log_yml_files[0]
                with open(log_yml_path) as f:
                    log_yml = yaml.safe_load(f)
            else:
                log_yml = {}
            log_yml_dict[subfolder][engine] = {"log_yml": log_yml}
    return log_yml_dict


def process_log_yml_dict(log_yml_dict):
    results_remote = {}
    for subfolder in list(log_yml_dict.keys()):
        print(f"Processing log yml file for {subfolder}")
        if subfolder in log_yml_dict:
            results_remote[subfolder] = {}
            for e in list(log_yml_dict[subfolder].keys()):
                # only if log_yml key is present
                if "log_yml" in log_yml_dict[subfolder][e]:
                    results_remote[subfolder][e] = utils.process_log_yml_dict(
                        log_yml_dict[subfolder][e]["log_yml"]
                    )
                else:
                    results_remote[subfolder][e] = {
                        "status": "ERROR",
                        "error_message": "log_yml key not found",
                        "exception_type": "KeyError",
                    }
    return results_remote


def remove_output_folders(extract_dir_dict):
    for _, extract_dirs in extract_dir_dict.items():
        os.chdir(extract_dirs["folder_dir"])
        if os.path.exists("results_remote"):
            shutil.rmtree("results_remote")
    return


def download_test_suite(
    url="https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip",
):
    """Download and unzip the test suite zip file, replacing existing files if they exist"""

    if os.path.exists("SBML_test_suite"):
        shutil.rmtree("SBML_test_suite")
    os.makedirs("SBML_test_suite", exist_ok=True)
    os.chdir("SBML_test_suite")
    url_filename = os.path.basename(url)

    # Download and extract the zip file
    response = requests.get(url)
    with open(url_filename, "wb") as f:
        f.write(response.content)
    with zipfile.ZipFile(url_filename, "r") as zip_ref:
        zip_ref.extractall()
    return


def process_cases(args):
    """
    process the test cases and write results out as a markdown table
    with links to the test case files online (as noted above the sedml files are actually in a zip file)
    with a summary of how many cases were tested and how many tests failed
    """

    # set up the markdown table
    column_labels = "case|valid-sbml|valid-sbml-units|valid-sedml|tellurium|xmlns-sbml-missing|tellurium-remote|copasi-remote"
    column_keys = "case|valid_sbml|valid_sbml_units|valid_sedml|tellurium_outcome|xmlns_sbml_missing|tellurium_remote_outcome|copasi_remote_outcome"
    mtab = utils.MarkdownTable(column_labels, column_keys)

    # set the path to the test suite
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

    if args.cases:
        subfolders = args.cases
    else:
        subfolders = [
            f
            for f in os.listdir(suite_path_abs)
            if os.path.isdir(os.path.join(suite_path_abs, f))
        ]
        if args.limit != 0:
            subfolders = subfolders[: args.limit]

    # submit remote runs and get results or use pickled results
    remote_results, remote_links = get_remote_results(
        suite_path=suite_path_abs,
        sbml_level_version=args.sbml_level_version,
        subfolders=subfolders,
    )

    for subfolder in subfolders:
        subfolder_dir = os.path.join(suite_path_abs, subfolder)
        os.chdir(subfolder_dir)
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
                if len(glob.glob(sedml_file_name)) > 0
                else []
            )

        if sbml_file_path == [] or sedml_file_path == []:
            print(
                f"Folder {subfolder} has no SBML or SED-ML files {args.sbml_level_version}"
            )
            continue

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

        # these give float errors when running the models in tellurium natively which leads to 'reset' errors in subsequent cases that would otherwise pass.
        # For now these cases are skipped.
        subfolders_float_errors = [
            "00952",
            "00953",
            "00962",
            "00963",
            "00964",
            "00965",
            "00966",
            "00967",
            "01588",
            "01590",
            "01591",
            "01599",
            "01605",
            "01627",
        ]

        if subfolder in subfolders_float_errors:
            print(f"Skipping subfolder {subfolder} with float errors")
            mtab["tellurium_outcome"] = (
                "<details><summary>skipped</summary>Case is skipped because it leads to a float error when trying to run it in tellurium natively, which leads to reset errors in subsequent cases that would otherwise pass.</details>"
            )

        elif subfolder in args.skip:
            print(f"Skipping subfolder {subfolder}")
            mtab["tellurium_outcome"] = (
                "<details><summary>skipped</summary>Case in skip list</details>"
            )

        else:
            mtab["tellurium_outcome"] = utils.test_engine(
                "tellurium", sedml_file_path
            )  # run tellurium directly

        sup.restore()

        mtab["xmlns_sbml_missing"] = utils.xmlns_sbml_attribute_missing(sedml_file_path)

        if subfolder in remote_results.keys():
            for e in list(remote_results[subfolder].keys()):
                print(f"Processing remote results for {subfolder} with engine {e}")

                if remote_results[subfolder][e]["error_message"] != "":
                    error_message = utils.safe_md_string(
                        remote_results[subfolder][e]["error_message"]
                    )
                    exception_type = utils.safe_md_string(
                        remote_results[subfolder][e]["exception_type"]
                    )
                    error_message_string = f"Error message: ```{error_message}```<br><br>Exception type: ```{exception_type}```"
                    info_submission = f'<details><summary>{remote_results[subfolder][e]["status"]}</summary>[Download]({remote_links[subfolder][e]["download"]})<br>[Logs]({remote_links[subfolder][e]["logs"]})<br>[View]({remote_links[subfolder][e]["view"]})<br><br>HTTP response: {str(remote_links[subfolder][e]["response"])}<br><br>{error_message_string}'
                else:
                    info_submission = f'<details><summary>{remote_results[subfolder][e]["status"]}</summary>[Download]({remote_links[subfolder][e]["download"]})<br>[Logs]({remote_links[subfolder][e]["logs"]})<br>[View]({remote_links[subfolder][e]["view"]})<br><br>HTTP response: {str(remote_links[subfolder][e]["response"])}'

                mtab_remote_outcome_key = f"{e}_remote_outcome"
                mtab[mtab_remote_outcome_key] = info_submission

        matplotlib.pyplot.close("all")  # supresses error from building up plots

    # give failure counts
    for key in [
        "valid_sbml",
        "valid_sbml_units",
        "valid_sedml",
    ]:
        mtab.add_count(key, lambda x: x is False, "n_fail={count}")
        mtab.transform_column(key, lambda x: "pass" if x else "FAIL")

    for key in [
        "tellurium_remote_outcome",
        "copasi_remote_outcome",
    ]:
        mtab.add_count(
            key, lambda x: "<details><summary>pass</summary>" in x, "pass={count}"
        )

    # add counts for cases and missing xmlns_sbml attributes
    mtab.add_count("case", lambda _: True, "n={count}")
    mtab.add_count("xmlns_sbml_missing", lambda x: x is True, "n={count}")

    # process engine outcomes column(s)
    mtab.simple_summary("tellurium_outcome")
    mtab.transform_column("tellurium_outcome")

    # write out to file
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print(f"Writing results to {args.output_file}")
    with open(args.output_file, "w") as fout:
        fout.write(md_description)
        mtab.write(fout)


def get_remote_results(
    suite_path, sbml_level_version, subfolders, use_pickle=True, remove_output=False
):
    """Run with directory pointing towards the location of the sedml and sbml files"""

    # pickle of all results_remote and remote_links together
    if use_pickle:
        os.chdir(suite_path)
        if os.path.exists("results_remote.p") and os.path.exists("remote_links.p"):
            results_remote = load_pickle("results_remote.p")
            remote_links = load_pickle("remote_links.p")
            return results_remote, remote_links
        else:
            print("No pickled results found. Running remote tests.")
    print("Running remote tests.")
    file_paths = get_test_suite_files_paths(suite_path, sbml_level_version, subfolders)
    run_test_suite_batch_remotely(["copasi", "tellurium"], file_paths, limit=0)
    remote_links = merge_pickled_links(file_paths, limit=0)
    extract_dir_dict = download_remote_test_suite_results(remote_links)
    log_yml_dict = create_log_yml_dict(extract_dir_dict)
    results_remote = process_log_yml_dict(log_yml_dict)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    # in suite_path, save pickled results
    os.chdir(suite_path)
    save_pickle(results_remote, "results_remote.p")
    save_pickle(remote_links, "remote_links.p")
    if remove_output:
        remove_output_folders(extract_dir_dict)
    return results_remote, remote_links


def remove_all_pickles_in_dir(dir_path):
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".p"):
                os.remove(os.path.join(root, file))
    return


def remove_all_pickles_in_folder(dir_path):
    for file in os.listdir(dir_path):
        if file.endswith(".p"):
            os.remove(os.path.join(dir_path, file))
    return


def remove_certain_pickles_in_dir(dir_path, subfolders):
    for subfolder in subfolders:
        pickle_file_path = os.path.join(dir_path, subfolder)
        remove_all_pickles_in_dir(pickle_file_path)
    return


def run_test_suite_with_retries(max_retries=10):
    retries = 0
    time_out = 10
    while retries < max_retries:
        try:
            process_cases(args)
            break
        except Exception as e:
            print(f"Error processing cases: {e}")
            retries += 1
            if retries < max_retries:
                print(
                    f"Retrying in {time_out} seconds... (Attempt {retries}/{max_retries})"
                )
                time.sleep(time_out)
            else:
                print("Max retries exceeded. Exiting script.")


if __name__ == "__main__":
    refresh = False
    if refresh:
        download_test_suite(
            url="https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip"
        )

    args = parse_arguments()
    args.suite_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "SBML_test_suite", "semantic"
    )
    if len(sys.argv) == 1:
        args.limit = 0

    run_test_suite_with_retries()
