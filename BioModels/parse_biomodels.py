#!/usr/bin/env python3

import os
import pickle
import re
import sys
import urllib

import matplotlib
import pyneuroml.sbml  # for validate_sbml_files
import pyneuroml.sedml  # for validate_sedml_files

sys.path.append("..")
import utils

md_description = """
Download and run validation tests on all the curated models from BioModels https://www.ebi.ac.uk/biomodels.
The final step is to run the model in tellurium,
only models specified in SBML with a matching SEDML file are run in tellurium.
Errors or validation failures are reported at each step.
Outputs to the Markdown Table below.

'valid-sbml-units' enforces strict unit checking, 'broken-ref' indicates that the SEDML file contained
a broken source='model.xml' reference which was corrected to the name of the model's provided SBML file.
"""

matplotlib.use("agg")  # prevent matplotlib from trying to open a window
API_URL: str = "https://www.ebi.ac.uk/biomodels"

out_format = "json"
max_count = 0  # 0 for unlimited

# local temporary storage of the model files
# this is independent of caching, and still happens when caching is turned off
# this allows the model to be executed and the files manually examined etc
tmp_dir = "tmplocalfiles"

# suppress stdout/err output from validation functions to make progress counter readable
suppress_stdout = True
suppress_stderr = True

# whether to replace "model.xml" in the sedml file with the name of the actual sbml file
fix_broken_ref = True

# skip tests that cause the script to be killed due to lack of RAM
# needs at least 8GB
skip = {}


def download_file(model_id, filename, output_file, cache):
    """
    request the given file and save it to disk
    """

    qfilename = urllib.parse.quote_plus(filename)

    response = cache.do_request(
        f"{API_URL}/model/download/{model_id}?filename={qfilename}"
    ).content

    with open(output_file, "wb") as fout:
        fout.write(response)


def replace_model_xml(sedml_path, sbml_filename):
    """
    if the SEDML refers to a generic "model.xml" file
    and the SBML file is not called this
    replace the SEDML reference with the actual SBML filename

    method used assumes 'source="model.xml"' will only
    occur in the SBML file reference
    which was true at time of testing on current BioModels release

    returns True if the SBML reference already seemed valid
    """

    if sbml_filename == "model.xml":
        return True

    with open(sedml_path, encoding="utf-8") as f:
        data = f.read()

    if 'source="model.xml"' not in data:
        return True

    data = data.replace('source="model.xml"', f'source="{sbml_filename}"')

    with open(f"{sedml_path}", "w", encoding="utf-8") as fout:
        fout.write(data)

    return False


def validate_sbml_file(model_id, mtab, info, cache, sup):
    """
    tasks relating to validating the SBML file
    return None to indicate aborting any further tests on this model
    otherwise return the SBML filename
    """

    # handle only single SBML files
    if not info["format"]["name"] == "SBML":
        mtab["valid_sbml"] = [
            "NonSBML",
            f"{info['format']['name']}:{info['files']['main']}",
        ]
        return None

    if len(info["files"]["main"]) > 1:
        mtab["valid_sbml"] = ["MultipleSBMLs", f"{info['files']['main']}"]
        return None

    if len(info["files"]["main"]) < 1:
        mtab["valid_sbml"] = ["NoSBMLs", f"{info['files']['main']}"]
        return None

    # download the sbml file
    sbml_file = info["files"]["main"][0]["name"]
    try:
        download_file(model_id, sbml_file, sbml_file, cache)
    except Exception as e:
        mtab["valid_sbml"] = ["DownloadFail", f"{sbml_file} {e}"]
        return None

    # validate the sbml file
    sup.suppress()  # suppress validation warning/error messages
    valid_sbml = pyneuroml.sbml.validate_sbml_files([sbml_file], strict_units=False)
    valid_sbml_units = pyneuroml.sbml.validate_sbml_files(
        [sbml_file], strict_units=True
    )
    sup.restore()

    mtab["valid_sbml"] = [
        "pass" if valid_sbml else "FAIL",
        f"[{sbml_file}]({API_URL}/{model_id}#Files)",
    ]
    mtab["valid_sbml_units"] = "pass" if valid_sbml_units else "FAIL"

    return sbml_file


def validate_sedml_file(model_id, mtab, info, cache, sup, sbml_file):
    """
    tasks relating to validating the SEDML file
    return None to indicate aborting any further tests on this model
    otherwise return the SEDML filename
    """

    # must have a SEDML file as well in order to be executed
    if "additional" not in info["files"]:
        mtab["valid_sedml"] = "NoSEDML"
        return None

    sedml_file = []
    for file_info in info["files"]["additional"]:
        pattern = "SED[-]?ML"
        target = f"{file_info['name']}|{file_info['description']}".upper()
        if re.search(pattern, target):
            sedml_file.append(file_info["name"])

    # require exactly one SEDML file
    if len(sedml_file) == 0:
        mtab["valid_sedml"] = "NoSEDML"
        return None

    if len(sedml_file) > 1:
        mtab["valid_sedml"] = ["MultipleSEDMLs", f"{sedml_file}"]
        return None

    # download sedml file
    sedml_file = sedml_file[0]
    try:
        download_file(model_id, sedml_file, sedml_file, cache)
    except Exception as e:
        mtab["valid_sedml"] = ["DownloadFail", f"{e}"]
        return None

    # if the sedml file contains a generic 'source="model.xml"' replace it with the sbml filename
    if fix_broken_ref:
        broken_ref = replace_model_xml(sedml_file, sbml_file)
        mtab["broken_ref"] = "pass" if broken_ref else "FAIL"
    else:
        mtab["broken_ref"] = "NA"

    sup.suppress()
    valid_sedml = pyneuroml.sedml.validate_sedml_files([sedml_file])
    sup.restore()
    mtab["valid_sedml"] = [
        "pass" if valid_sedml else "FAIL",
        f"[{sedml_file}]({API_URL}/{model_id}#Files)",
    ]

    return sedml_file


def main():
    """
    download the BioModel model files, run various validation steps
    report the results as a markdown table README file with a summary row at the top
    """

    # caching is used to prevent the need to download the same responses from the remote server multiple times during testing
    # mode="off" to disable caching, "store" to wipe and store fresh results, "reuse" to use the stored cache
    cache = utils.RequestCache(mode="auto", direc="cache")

    # accumulate results in columns defined by keys which correspond to the local variable names to be used below
    # to allow automated loading into the columns
    column_labels = "Model     |valid-sbml|valid-sbml-units|valid-sedml|broken-ref|tellurium|tellurium-remote|copasi-remote"
    column_keys = "model_desc|valid_sbml|valid_sbml_units|valid_sedml|broken_ref|tellurium_outcome|tellurium_remote_outcome|copasi_remote_outcome"
    mtab = utils.MarkdownTable(column_labels, column_keys)

    # allow stdout/stderr from validation tests to be suppressed to improve progress count visibility
    sup = utils.SuppressOutput(stdout=suppress_stdout, stderr=suppress_stderr)

    # get list of all available models
    model_ids = cache.do_request(
        f"{API_URL}/model/identifiers?format={out_format}"
    ).json()["models"]
    count = 0
    starting_dir = os.getcwd()

    for model_id in model_ids:
        pickle_name = f"{model_id}_mtab.p"
        pickle_path = os.path.join(starting_dir, tmp_dir, model_id, pickle_name)
        if os.path.exists(pickle_path) and use_pickles:
            print(f"\r{model_id} {count}/{len(model_ids)}       ", end="")
            print(f"loading {pickle_path}...")
            mtab_dict = pickle.load(open(pickle_path, "rb"))
            mtab.new_row()
            mtab = mtab_dict["mtab_row"]
            continue
        # allow testing on a small sample of models
        if max_count > 0 and count >= max_count:
            break
        count += 1
        print(f"\r{model_id} {count}/{len(model_ids)}       ", end="")

        # only process curated models
        # BIOMD ids should be the curated models
        if "BIOMD" not in model_id:
            continue

        # skip if on the list to be skipped
        if count in skip or model_id in skip:
            continue

        # from this point the model will create an output row even if not all tests are run
        mtab.new_row()  # append empty placeholder row
        info = cache.do_request(f"{API_URL}/{model_id}?format={out_format}").json()

        if len(info["name"]) > 36:
            model_summary = (
                f"[{model_id}]({API_URL}/{model_id})<br/><sup>{info['name'][:30]}</sup>"
            )
            model_details = f"<sup>{info['name']}</sup>"
            mtab["model_desc"] = mtab.make_fold(model_summary, model_details)
        else:
            mtab["model_desc"] = (
                f"[{model_id}]({API_URL}/{model_id})<br/><sup>{info['name']}</sup>"
            )

        # make temporary downloads of the sbml and sedml files
        model_dir = os.path.join(starting_dir, tmp_dir, model_id)
        os.makedirs(model_dir, exist_ok=True)
        os.chdir(model_dir)

        # sbml file validation tasks, includes downloading a local copy
        sbml_file = validate_sbml_file(model_id, mtab, info, cache, sup)
        if not sbml_file:
            continue  # no further tests possible

        sedml_file = validate_sedml_file(model_id, mtab, info, cache, sup, sbml_file)
        if not sedml_file:
            continue  # no further tests possible

        # run the validation functions on the sbml and sedml files
        print(f"\ntesting {sbml_file}...")
        sup.suppress()
        mtab["tellurium_outcome"] = utils.test_engine("tellurium", sedml_file)
        sup.restore()

        engine_keys = ["copasi", "tellurium"]
        test_folder = "tests"
        d1_plots_remote_dir = os.path.join(test_folder, "d1_plots_remote")
        results_remote = utils.run_biosimulators_remotely(
            engine_keys,
            sedml_file_name=sedml_file,
            sbml_file_name=sbml_file,
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

        # stop matplotlib plots from building up
        matplotlib.pyplot.close()

        mtab_dict = {"mtab_row": mtab, "results_remote": results_remote}
        pickle.dump(mtab_dict, open(pickle_name, "wb"))

    print()  # end progress counter, go to next line of stdout

    # show total cases processed
    mtab.add_summary("model_desc", f"n={mtab.n_rows()}")

    # count occurrences of each cell value, convert to final form
    for key in [
        "valid_sbml",
        "valid_sbml_units",
        "valid_sedml",
        "broken_ref",
        "tellurium_outcome",
        "tellurium_remote_outcome",
        "copasi_remote_outcome",
    ]:
        mtab.simple_summary(key)
        mtab.transform_column(key)

    # convert engine error messages to foldable readable form
    # calculate error category counts for summary row
    # mtab.process_engine_outcomes('tellurium','tellurium_outcome')

    # write out to file
    os.chdir(starting_dir)
    with open("README.md", "w", encoding="utf-8") as fout:
        fout.write(md_description)
        mtab.write(fout)


if __name__ == "__main__":
    use_pickles = True
    main()
