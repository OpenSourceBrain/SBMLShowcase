import os
import re
import shutil
import sys
import urllib

sys.path.append("..")
import utils

engines = utils.ENGINES
API_URL: str = "https://www.ebi.ac.uk/biomodels"

out_format = "json"
max_count = 0  # 0 for unlimited
tmp_dir = "tmplocalfiles"
suppress_stdout = True
suppress_stderr = True
fix_broken_ref = True
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


def download_sbml_file(model_id, info, cache):
    sbml_file = info["files"]["main"][0]["name"]
    try:
        download_file(model_id, sbml_file, sbml_file, cache)
    except Exception as e:
        raise Exception(f"Error downloading {sbml_file} for {model_id}: {e}")

    return sbml_file


def download_sedml_file(model_id, info, cache, sbml_file):
    if "additional" not in info["files"]:
        print(f"no additional files for {model_id}")

    sedml_file = []
    for file_info in info["files"]["additional"]:
        pattern = "SED[-]?ML"
        target = f"{file_info['name']}|{file_info['description']}".upper()
        if re.search(pattern, target):
            sedml_file.append(file_info["name"])
    sedml_file = sedml_file[0]

    try:
        download_file(model_id, sedml_file, sedml_file, cache)
    except Exception as e:
        print(f"Error downloading {sedml_file} for {model_id}: {e}")

    # if the sedml file contains a generic 'source="model.xml"' replace it with the sbml filename
    if fix_broken_ref:
        replace_model_xml(sedml_file, sbml_file)

    return sedml_file


def main():
    """
    download the BioModel model files, run various validation steps
    report the results as a markdown table README file with a summary row at the top
    """

    # mode="off" to disable caching, "store" to wipe and store fresh results, "reuse" to use the stored cache
    cache = utils.RequestCache(mode="store", direc="cache")
    count = 0
    starting_dir = os.getcwd()

    model_ids = cache.do_request(
        f"{API_URL}/model/identifiers?format={out_format}"
    ).json()["models"]
    if biomodel_id_list is not None:
        model_ids = biomodel_id_list

    for model_id in model_ids:
        if max_count > 0 and count >= max_count:
            break
        count += 1
        print(f"\r{model_id} {count}/{len(model_ids)}       ", end="")

        # BIOMD ids should be the curated models
        if "BIOMD" not in model_id:
            continue
        if count in skip or model_id in skip:
            continue

        info = cache.do_request(f"{API_URL}/{model_id}?format={out_format}").json()

        tmp_model_dir = os.path.join(starting_dir, tmp_dir, model_id)
        os.makedirs(tmp_model_dir, exist_ok=True)
        os.chdir(tmp_model_dir)

        sbml_file = download_sbml_file(model_id, info, cache)
        sbml_file_path = os.path.join(tmp_model_dir, sbml_file)
        if not sbml_file:
            continue
        sedml_file = download_sedml_file(model_id, info, cache, sbml_file)
        sedml_file_path = os.path.join(tmp_model_dir, sedml_file)
        if not sedml_file:
            continue

        print(f"\ntesting {sbml_file}...")

        new_subfolder = model_id
        new_directory = os.path.join(starting_dir, new_subfolder)
        os.makedirs(new_directory, exist_ok=True)

        new_sbml_file_path = os.path.join(new_directory, os.path.basename(sbml_file))
        new_sedml_file_path = os.path.join(new_directory, os.path.basename(sedml_file))

        paths_exist = os.path.exists(new_sbml_file_path) and os.path.exists(
            new_sedml_file_path
        )
        if use_original_files or not paths_exist:
            print(
                f"Copying {sbml_file} and {sedml_file} to {starting_dir}/{new_subfolder}"
            )
            shutil.copy(sbml_file_path, new_sbml_file_path)
            shutil.copy(sedml_file_path, new_sedml_file_path)

        os.chdir(new_directory)
        print(f"Changed to {new_directory}")

        engine_ids = list(engines.keys())

        test_folder = "tests"
        utils.run_biosimulators_remotely_and_locally(
            engine_ids,
            os.path.basename(sedml_file_path),
            os.path.basename(sbml_file_path),
            os.path.join(test_folder, "d1_plots_remote"),
            os.path.join(test_folder, "d1_plots_local"),
            test_folder=test_folder,
        )

        shutil.rmtree(tmp_model_dir)


if __name__ == "__main__":
    use_original_files = False  # False allows you to tweak the SED-ML files before running. True overwrites the test files with the original BioModels files.
    biomodel_id_list = [
        "BIOMD0000000001",
        "BIOMD0000000138",
        "BIOMD0000000724",
        "BIOMD0000001077",
    ]
    main()
