import glob
import hashlib
import json
import os
import pickle
import random
import re
import shutil
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import docker
import libsbml
import libsedml
import pandas as pd
import requests
import yaml
from pymetadata import omex
from pyneuroml import biosimulations, tellurium
from requests.exceptions import HTTPError

ENGINES = {
    "amici": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_AMICI/",
        "status": "",
        "name": "AMICI",
    },
    "brian2": {
        "formats": [("nml", "sedml"), ("lems", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_pyNeuroML/",
        "status": "",
        "name": "Brian 2",
    },
    "bionetgen": {
        "formats": [("bngl", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_BioNetGen/",
        "status": "",
        "name": "BioNetGen",
    },
    "boolnet": {
        "formats": [("sbmlqual", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_BoolNet/",
        "status": "",
        "name": "BoolNet",
    },
    "cbmpy": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_CBMPy/",
        "status": "",
        "name": "CBMPy",
    },
    "cobrapy": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_COBRApy/",
        "status": "Only allows steady state simulations",
        "name": "COBRApy",
    },
    "copasi": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_COPASI/",
        "status": "",
        "name": "COPASI",
    },
    "gillespy2": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_GillesPy2/",
        "status": "",
        "name": "GillesPy2",
    },
    "ginsim": {
        "formats": [("sbmlqual", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_GINsim/",
        "status": "",
        "name": "GINsim",
    },
    "libsbmlsim": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_LibSBMLSim/",
        "status": "",
        "name": "LibSBMLSim",
    },
    "masspy": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_MASSpy/",
        "status": "",
        "name": "MASSpy",
    },
    "netpyne": {
        "formats": [("nml", "sedml"), ("lems", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_pyNeuroML/",
        "status": "",
        "name": "NetPyNE",
    },
    "neuron": {
        "formats": [("nml", "sedml"), ("lems", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_pyNeuroML/",
        "status": "",
        "name": "NEURON",
    },
    "opencor": {
        "formats": [("cellml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_OpenCOR/",
        "status": "",
        "name": "OpenCOR",
    },
    "pyneuroml": {
        "formats": [("nml", "sedml"), ("lems", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_pyNeuroML/",
        "status": "",
        "name": "pyNeuroML",
    },
    "pysces": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_PySCeS/",
        "status": "",
        "name": "PySCeS",
    },
    "rbapy": {
        "formats": [("rbapy", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_RBApy/",
        "status": "",
        "name": "RBApy",
    },
    "smoldyn": {
        "formats": [("smoldyn", "sedml")],
        "url": "https://smoldyn.readthedocs.io/en/latest/python/api.html#sed-ml-combine-biosimulators-api",
        "status": "",
        "name": "Smoldyn",
    },
    "tellurium": {
        "formats": [("sbml", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_tellurium/",
        "status": "",
        "name": "Tellurium",
    },
    "vcell": {
        "formats": [("sbml", "sedml"), ("bngl", "sedml")],
        "url": "https://github.com/virtualcell/vcell",
        "status": "",
        "name": "VCell",
    },
    "xpp": {
        "formats": [("xpp", "sedml")],
        "url": "https://docs.biosimulators.org/Biosimulators_XPP/",
        "status": "",
        "name": "XPP",
    },
}


TYPES = {
    "sbml": "SBML",
    "sedml": "SED-ML",
    "nml": "NeuroML",
    "lems": "LEMS",
    "sbmlqual": "SBML-qual",
    "bngl": "BNGL",
    "rbapy": "RBApy",
    "xpp": "XPP",
    "smoldyn": "Smoldyn",
    "cellml": "CellML",
    "xml": "XML",
}

# define the column headers for the markdown table
ERROR = "Error"
PASS_FAIL = "pass / FAIL"
TYPE = "Type"
COMPAT = "Compatibility"
D1 = "d1"
ENGINE = "Engine"

# define error categories for detailed error counting per engine
# (currently only tellurium)
# key is the tag/category used to report the category, value is a regex matching the error message
# see MarkdownTable.process_engine_outcomes
# TODO: use error categories in process_log_yml_dict
error_categories = {
    "tellurium": {
        "algebraic": "^Unable to support algebraic rules.",
        "delay": "^Unable to support delay differential equations.",
        "ASTNode": "^Unknown ASTNode type of",
        "stochiometry": "^Mutable stochiometry for species which appear multiple times in a single reaction",
        "float": "^'float' object is not callable",
        "SpeciesRef": "is not a named SpeciesReference",
        "reset": "reset",
        "SEDMLfile": "^failed to validate SEDML file",
        "NoSBMLelement": "^No sbml element exists",
        "CV_ERR_FAILURE": "CV_ERR_FAILURE",
        "CV_TOO_MUCH_WORK": "CV_TOO_MUCH_WORK",
        "CV_CONV_FAILURE": "CV_CONV_FAILURE",
        "CV_ILL_INPUT": "CV_ILL_INPUT",
        "OutOfRange": "list index out of range",
    },
}


def get_entry_format(file_path, file_type):
    """
    Get the entry format for a file.

    Args:
        file_path (:obj:`str`): path to the file
        file_type (:obj:`str`): type of the file

    Returns:
        :obj:`str`: entry format
    """

    if file_type == "SBML":
        file_l = libsbml.readSBML(file_path).getLevel()
        file_v = libsbml.readSBML(file_path).getVersion()
    elif file_type == "SEDML":
        file_l = libsedml.readSedML(file_path).getLevel()
        file_v = libsedml.readSedML(file_path).getVersion()
    else:
        raise ValueError(f"Invalid file type: {file_type}")

    file_entry_format = f"{file_type}_L{file_l}V{file_v}"
    entry_formats = [f.name for f in omex.EntryFormat]
    if file_entry_format not in entry_formats:
        file_entry_format = file_type

    return file_entry_format


def temp_sedml_file_if_not_empty(sedml_filepath, temp_sedml_filepath):
    """
    If the temp_sedml_filepath is not empty, return its content, otherwise return the original content of the sedml file
    """
    sedstr = ""

    if temp_sedml_filepath:
        if os.path.exists(temp_sedml_filepath):
            with open(temp_sedml_filepath, "r") as file:
                sedstr = file.read()

    if sedstr == "":
        with open(sedml_filepath, "r") as file:
            sedstr = file.read()

    return sedstr


def add_xmlns_sbml_attribute(sedml_filepath, sbml_filepath, temp_sedml_filepath=None):
    """
    add an xmlns:sbml attribute to the sedml file that matches the sbml file
    raise an error if the attribute is already present
    output fixed file to output_filepath which defaults to sedml_filepath

    If no temp_sedml_filepath is provided, the original sedml file is overwritten.
    """

    sed_str = temp_sedml_file_if_not_empty(sedml_filepath, temp_sedml_filepath)

    m = re.search(r"<sedML[^>]*>", sed_str)

    if m is None:
        raise ValueError(
            f"Invalid SedML file: main <sedML> tag not found in {sedml_filepath}"
        )

    if "xmlns:sbml" in m.group():
        raise ValueError(
            f"xmlns:sbml attribute already present in file {sedml_filepath}"
        )

    with open(sbml_filepath, "r") as file:
        sbml_str = file.read()

    sbml_xmlns = re.search(r'xmlns="([^"]*)"', sbml_str).group(1)
    missing_sbml_attribute = 'xmlns:sbml="' + sbml_xmlns + '"'

    sed_str = re.sub(r"<sedML ", r"<sedML " + missing_sbml_attribute + " ", sed_str)

    if temp_sedml_filepath is None:
        temp_sedml_filepath = sedml_filepath

    with open(temp_sedml_filepath, "w") as fout:
        fout.write(sed_str)


def add_xmlns_fbc_attribute(sedml_filepath, sbml_filepath, temp_sedml_filepath=None):
    """
    Adds an xmlns:fbc attribute to the SED-ML file.

    If a temp_sedml_filepath (which could already contain a xmlns:sbml fix) is provided,
    this instead of the original SED-ML file is used.
    """

    sedstr = temp_sedml_file_if_not_empty(sedml_filepath, temp_sedml_filepath)

    m = re.search(r"<sedML[^>]*>", sedstr)

    if m is None:
        raise ValueError(
            f"Invalid SedML file: main <sedML> tag not found in {sedml_filepath}"
        )

    location = m.span()[1] - 1
    with open(sbml_filepath, "r") as file:
        sbml_str = file.read()

    fbc_xmlns = re.search(r'xmlns:fbc="([^"]*)"', sbml_str).group(1)
    missing_fbc_attribute = 'xmlns:fbc="' + fbc_xmlns + '"'
    sedstr = sedstr[:location] + " " + missing_fbc_attribute + sedstr[location:]

    if temp_sedml_filepath is None:
        temp_sedml_filepath = sedml_filepath

    with open(temp_sedml_filepath, "w") as fout:
        fout.write(sedstr)


def xmlns_sbml_attribute_missing(sedml_filepath):
    """
    True if the xmlns:sbml attribute is missing from the main sedml tag
    """

    with open(sedml_filepath, "r") as file:
        sedstr = file.read()

    m = re.search(r"<sedML[^>]*>", sedstr)

    if m is None:
        raise ValueError(
            f"Invalid SedML file: main <sedML> tag not found in {sedml_filepath}"
        )

    if "xmlns:sbml" not in m.group():
        return True
    else:
        return False


def xmlns_fbc_attribute_missing(sbml_filepath, sedml_filepath):
    """
    True if the xmlns:fbc attribute is missing from the main sedml tag of the SED-ML file but present in the SBML file
    """

    with open(sbml_filepath, "r", encoding="utf-8") as file:
        sbmlstr = file.read()

    with open(sedml_filepath, "r", encoding="utf-8") as file:
        sedstr = file.read()

    sbmlstr_fbc = re.search(r'xmlns:fbc="([^"]*)"', sbmlstr)
    sedstr_fbc = re.search(r'xmlns:fbc="([^"]*)"', sedstr)

    if sbmlstr_fbc and not sedstr_fbc:
        return True
    else:
        return False


def get_temp_file():
    """
    create a temporary filename in the current working directory
    """
    return f"tmp{random.randrange(1000000)}"


def remove_spaces_from_filename(file_path):
    """
    create another file with the same content but with filename spaces replaced by underscores
    """
    dir_name = os.path.dirname(file_path)
    if " " in dir_name:
        raise ValueError(f"File directory path should not contain spaces: {dir_name}")
    old_filename = os.path.basename(file_path)
    if " " not in old_filename:
        return file_path
    if " " in old_filename:
        new_filename = old_filename.replace(" ", "_")
        new_file_path = os.path.join(dir_name, new_filename)
        shutil.copy(file_path, new_file_path)
        return new_file_path


def create_omex(
    sedml_filepath,
    sbml_filepath,
    omex_filepath=None,
    silent_overwrite=True,
    add_missing_xmlns=True,
):
    """
    wrap a sedml and an sbml file in a combine archive omex file
    overwrite any existing omex file
    """

    # provide an omex filepath if not specified
    if not omex_filepath:
        if sedml_filepath.endswith(".sedml"):
            omex_filepath = Path(sedml_filepath[:-6] + ".omex")
        elif sedml_filepath.endswith(".xml"):
            omex_filepath = Path(sedml_filepath[:-4] + ".omex")
        else:
            omex_filepath = Path(sedml_filepath + ".omex")

    # suppress pymetadata "file exists" warning by preemptively removing existing omex file
    if os.path.exists(omex_filepath) and silent_overwrite:
        os.remove(omex_filepath)

    tmp_sedml_filepath = get_temp_file()

    if add_missing_xmlns:
        xmlns_sbml_missing = xmlns_sbml_attribute_missing(sedml_filepath)
        xmlns_fbc_missing = xmlns_fbc_attribute_missing(sbml_filepath, sedml_filepath)
        if xmlns_sbml_missing:
            add_xmlns_sbml_attribute(sedml_filepath, sbml_filepath, tmp_sedml_filepath)
        if xmlns_fbc_missing:
            add_xmlns_fbc_attribute(sedml_filepath, sbml_filepath, tmp_sedml_filepath)
        if xmlns_sbml_missing or xmlns_fbc_missing:
            sedml_filepath = tmp_sedml_filepath

    sbml_file_entry_format = get_entry_format(sbml_filepath, "SBML")
    sedml_file_entry_format = get_entry_format(sedml_filepath, "SEDML")

    # wrap sedml+sbml files into an omex combine archive
    om = omex.Omex()
    om.add_entry(
        entry=omex.ManifestEntry(
            location=sedml_filepath,
            format=getattr(omex.EntryFormat, sedml_file_entry_format),
            master=True,
        ),
        entry_path=Path(os.path.basename(sedml_filepath)),
    )
    om.add_entry(
        entry=omex.ManifestEntry(
            location=sbml_filepath,
            format=getattr(omex.EntryFormat, sbml_file_entry_format),
            master=False,
        ),
        entry_path=Path(os.path.basename(sbml_filepath)),
    )
    om.to_omex(Path(omex_filepath))

    if os.path.exists(tmp_sedml_filepath):
        os.remove(tmp_sedml_filepath)

    return omex_filepath


def read_log_yml(log_filepath):
    """
    read the log YAML file if it exists
    return the exception message as a string
    """
    if not os.path.isfile(log_filepath):
        return None
    with open(log_filepath) as f:
        ym = yaml.safe_load(f)
    return ym["exception"]["message"]


def find_files(directory, extension):
    files = glob.glob(f"{directory}/**/*{extension}", recursive=True)
    return files


def move_d1_files(file_paths, plot_dir="d1_plots"):
    for fpath in file_paths:
        # find engine.keys() in the file path and asign to engine
        engine = next((e for e in ENGINES.keys() if e in fpath), "unknown")
        new_file_path = os.path.join(plot_dir, f"{engine}_{os.path.basename(fpath)}")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir, exist_ok=True)
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        print(f"Moving {fpath} to {new_file_path}")
        shutil.move(fpath, new_file_path)


def find_file_in_dir(file_name, directory):
    """
    Searches for a specific file in a given directory and its subdirectories.

    Parameters:
    file_name (str): The name of the file to search for.
    directory (str): The directory to search in.

    Returns:
    str: The path of the found file. If the file is not found, returns None.
    """

    list_of_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file == file_name:
                file_path = os.path.join(root, file)
                list_of_files.append(file_path)
    return list_of_files


def d1_plots_dict(d1_plots_path="d1_plots"):
    """
    Create a dictionary with engine names as keys and d1 plot paths as values.
    """
    d1_plots = find_files(d1_plots_path, ".pdf")
    # to fix broken links in output table after changing the file structure, remove the first two parts of the path
    d1_plots = [os.path.join(*Path(d1_plot).parts[1:]) for d1_plot in d1_plots]
    d1_plots_dict = {
        e: d1_plot for e in ENGINES.keys() for d1_plot in d1_plots if e in d1_plot
    }

    return d1_plots_dict


def create_hyperlink(path, title=None):
    """
    Create a hyperlink to a file or folder. If the path is None, return None.
    Title is the basename of the path.
    """
    if path:
        if title is None:
            title = os.path.basename(path)
        return f'<a href="{path}">{title}</a>'
    else:
        return None


def ansi_to_html(text):
    if text is not None:
        text_message = re.findall(r'"([^"]*)"', text)
        if len(text_message) > 0:
            text = text_message
            text = bytes(text[0], "utf-8").decode("unicode_escape")
        text = text.replace("|", "")

        # # for any text with "<*>" remove "<" as well as ">" but leave wildcard text *
        text = re.sub(r"<([^>]*)>", r"\1", text)

        # replace color codes with html color codes
        text = text.replace("\x1b[33m", "")
        text = text.replace("\x1b[31m", "")

        # # remove .\x1b[0m
        text = text.replace("\x1b[0m", "")

        # find first "." or ":" after "<span*" and add "</span>"after it
        pattern = r'(<span style="[^"]*">[^.:]*)([.:])'
        replacement = r"\1\2</span>"
        text = re.sub(pattern, replacement, text, count=1)

        # bullet points and new lines
        text = text.replace("\r\n  - ", "</li><li>")
        text = text.replace("\r\n", "<br>")
        text = text.replace("\n", "<br>")

        # BioSimulatorsWarning:  two <br> tags after
        text = text.replace(
            "BioSimulatorsWarning:", "<br><br>BioSimulatorsWarning:<br><br>"
        )
        text = text.replace(
            "warnings.warn(termcolor.colored(message, Colors.warning.value), category)",
            "<br>",
        )

        return text


def check_file_compatibility_test(engine, model_filepath, experiment_filepath):
    """
    Check if the file extensions suggest the file types are compatible with the engine.
    Only .sedml and .sbml files, and .xml files with 'sedml' and/or 'sbml' in their filename
    are considered at this moment. It can be extended to other cases if needed in the future.
    """
    file_extensions = get_filetypes(model_filepath, experiment_filepath)
    engine_filetypes_tuple_list = ENGINES[engine]["formats"]
    engine_name = ENGINES[engine]["name"]
    flat_engine_filetypes_tuple_list = [
        item
        for sublist in engine_filetypes_tuple_list
        for item in sublist
        if sublist != "unclear"
    ]
    compatible_filetypes = [
        TYPES[i] for i in flat_engine_filetypes_tuple_list if i in list(TYPES.keys())
    ]
    unique_compatible_filetpyes = list(set(compatible_filetypes))

    unique_compatible_filetpyes_strings = (
        ", ".join(unique_compatible_filetpyes[:-1])
        + " and "
        + unique_compatible_filetpyes[-1]
        if len(unique_compatible_filetpyes) > 1
        else unique_compatible_filetpyes[0]
    )

    file_types = [TYPES[i] for i in file_extensions]
    filetypes_strings = (
        ", ".join(file_types[:-1]) + " and " + file_types[-1]
        if len(file_types) > 1
        else file_types[0]
    )

    if (
        file_extensions == ("sbml", "sedml")
        and file_extensions not in engine_filetypes_tuple_list
    ):
        return "FAIL", (
            f"The file extensions {file_extensions} suggest the input file types are {filetypes_strings} which is not compatible with {engine_name}.<br><br>{unique_compatible_filetpyes_strings} are compatible with {engine_name}."
        )

    if file_extensions in engine_filetypes_tuple_list:
        return "pass", (
            f"The file extensions {file_extensions} suggest the input file types are {filetypes_strings}.<br><br> {unique_compatible_filetpyes_strings} are compatible with {engine_name}."
        )

    if "xml" in file_extensions:
        model_sbml = "sbml" in model_filepath
        model_sedml = "sedml" in model_filepath
        experiment_sbml = "sbml" in experiment_filepath
        experiment_sedml = "sedml" in experiment_filepath

        if model_sbml and experiment_sbml and experiment_sedml and not model_sedml:
            file_types_tuple = ("sbml", "sedml")
            file_types = [TYPES[i] for i in file_types_tuple]
            filetypes_strings = (
                ", ".join(file_types[:-1]) + " and " + file_types[-1]
                if len(file_types) > 1
                else file_types[0]
            )
            if file_types_tuple in engine_filetypes_tuple_list:
                return "pass", (
                    f"The filenames '{model_filepath}' and '{experiment_filepath}' suggest the input files are {filetypes_strings} which is compatible with {engine_name}.<br><br>{unique_compatible_filetpyes_strings} are compatible with {engine_name}."
                )
            else:
                return "FAIL", (
                    f"The filenames '{model_filepath}' and '{experiment_filepath}' suggest the input files are {filetypes_strings} which is not compatible with {engine_name}.<br><br>{unique_compatible_filetpyes_strings} are compatible with {engine_name}."
                )
        else:
            return "unsure", (
                f"The file extensions {file_extensions} suggest the input file types may not be compatibe with {engine_name}.<br><br>{unique_compatible_filetpyes_strings} are compatible with {engine_name}."
            )
    else:
        return "unsure", (
            f"The file extensions {file_extensions} suggest the input file types may not be compatibe with {engine_name}.<br><br>{unique_compatible_filetpyes_strings} are compatible with {engine_name}."
        )


def collapsible_content(content, title="Details"):
    """
    Create a collapsible content section in markdown format

    Input: content, title
    """
    if content:
        return f"<details><summary>{title}</summary>{content}</details>"
    else:
        return f"{title}"


def get_filetypes(model_filepath, simulation_filepath):
    """
    Get the filetypes of the model and simulation files

    Input: model_filepath, simulation_filepath
    Output: tuple of filetypes
    """
    model_ext = os.path.splitext(model_filepath)[-1].lstrip(".")
    simulation_ext = os.path.splitext(simulation_filepath)[-1].lstrip(".")

    return (model_ext, simulation_ext)


def delete_output_folder(output_dir):
    """
    # Delete the output folder and its contents
    """
    for file_name in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def run_biosimulators_remote(engine, sedml_filepath, sbml_filepath):
    """
    put the sedml and sbml file into an omex archive
    run it remotely using biosimulators
    """

    # put the sedml and sbml into a combine archive
    omex_filepath = create_omex(sedml_filepath, sbml_filepath)
    omex_file_name = os.path.basename(omex_filepath)

    # get the version of the engine
    engine_version = biosimulations.get_simulator_versions(engine)

    sim_dict = {
        "name": omex_file_name,
        "simulator": engine,
        "simulatorVersion": engine_version[engine][-1],  # get the latest version
        "cpus": 1,
        "memory": 8,
        "maxTime": 20,
        "envVars": [],
        "purpose": "academic",
        "email": "",
    }

    try:
        results_urls = biosimulations.submit_simulation_archive(
            archive_file=omex_file_name, sim_dict=sim_dict
        )
        results_urls["response"] = results_urls["response"].status_code
    except Exception as exception_message:
        print(
            f"There was an error submitting the simulation archive:{exception_message}"
        )
        results_urls = {
            "response": "",
            "view": "",
            "download": "",
            "logs": "",
            "exception": exception_message,
        }
        return results_urls

    return results_urls


def get_remote_results(engine, download_link, output_dir="remote_results"):
    filepath_results = download_file_from_link(engine, download_link)
    extract_dir = os.path.join(os.getcwd(), output_dir, engine)
    shutil.unpack_archive(filepath_results, extract_dir=extract_dir)
    os.remove(filepath_results)
    return extract_dir


def rename_files_in_extract_dir(extract_dir, engine):
    log_yml_path = find_file_in_dir("log.yml", extract_dir)[0]
    new_file_name = f"{engine}_log.yml"
    root = os.path.dirname(log_yml_path)
    new_file_path = os.path.join(root, new_file_name)
    if os.path.exists(new_file_path):
        os.remove(new_file_path)
    os.rename(log_yml_path, new_file_path)

    return extract_dir


def run_biosimulators_docker(
    engine, sedml_filepath, sbml_filepath, output_dir="output", chown_outputs=True
):
    """
    put the sedml and sbml file into an omex archive
    run it locally using a biosimulators docker
    categorise an error message in the log file
    """

    # put the sedml and sbml into a combine archive
    omex_filepath = create_omex(sedml_filepath, sbml_filepath)
    log_yml_path = os.path.join(output_dir, "log.yml")
    log_yml_dict = {}
    exception_message = ""

    try:
        biosimulators_core(engine, omex_filepath, output_dir=output_dir)
    except Exception as e:
        exception_message = str(e)

    # ensure outputs are owned by the user
    if "getuid" in dir(os) and chown_outputs:
        uid = os.getuid()
        gid = os.getgid()
        os.system(f"sudo chown -R {uid}:{gid} {output_dir}")

    if os.path.exists(log_yml_path):
        with open(log_yml_path) as f:
            log_yml_dict = yaml.safe_load(f)

    # to deal with vcell like cases where there is a log_yml with status SUCCEEDED but a detailedErrorLog.txt with "RuntimeError"
    detailed_error_log_dict = {}
    if os.path.exists(os.path.join(output_dir, "detailedErrorLog.txt")):
        with open(os.path.join(output_dir, "detailedErrorLog.txt")) as f:
            detailed_error_log = f.read()
        if "RuntimeException" in detailed_error_log:
            detailed_error_log_dict["status"] = "FAIL"
            detailed_error_log_dict["error_message"] = "Runtime Exception"
            return {
                "exception_message": exception_message,
                "log_yml": log_yml_dict,
                "detailed_error_log": detailed_error_log_dict,
            }
        if "RuntimeException" in detailed_error_log:
            detailed_error_log_dict["status"] = "FAIL"
            detailed_error_log_dict["error_message"] = "Runtime Exception"

    return {
        "exception_message": exception_message,
        "log_yml": log_yml_dict,
        "detailed_error_log": detailed_error_log_dict,
    }


def biosimulators_core(engine, omex_filepath, output_dir=None):
    """
    run the omex file using biosimulators
    calls biosimulators via docker locally
    assumes local docker is setup
    engine can be any string that matches a biosimulators docker "URI":
    ghcr.io/biosimulators/{engine}

    omex_filepath: the OMEX file to run
    output_dir: folder to write the simulation outputs to
    """

    omex_filepath_no_spaces = remove_spaces_from_filename(omex_filepath)

    # directory containing omex file needs mapping into the container as the input folders
    omex_dir = os.path.dirname(os.path.abspath(omex_filepath_no_spaces))
    omex_file = os.path.basename(os.path.abspath(omex_filepath_no_spaces))

    mount_in = docker.types.Mount("/root/in", omex_dir, type="bind", read_only=True)

    # we want the output folder to be different to the input folder
    # to avoid the "file already exists" type error
    if not output_dir:
        output_dir = os.path.join(omex_dir, "output")

    os.makedirs(output_dir, exist_ok=True)

    mount_out = docker.types.Mount("/root/out", output_dir, type="bind")
    client = docker.from_env()
    client.containers.run(
        f"ghcr.io/biosimulators/{engine}",
        mounts=[mount_in, mount_out],
        command=f"-i '/root/in/{omex_file}' -o /root/out",
        auto_remove=True,
    )
    client.containers.run(
        f"ghcr.io/biosimulators/{engine}",
        mounts=[mount_in, mount_out],
        command=f"-i '/root/in/{omex_file}' -o /root/out",
        auto_remove=True,
    )

    if os.path.exists(omex_filepath_no_spaces):
        os.remove(omex_filepath_no_spaces)


def test_engine(engine, filename, error_categories=error_categories):
    """
    test running the file with the given engine
    return category tagged error message, or "pass" if no error was raised
    """

    unknown_engine = False
    try:
        if engine == "tellurium":
            print(f"Running tellurium natively for {filename}", file=sys.__stdout__)
            tellurium.run_from_sedml_file([filename], ["-outputdir", "none"])
            return "pass"  # no errors
        # elif engine == "some_other_engine":
        #    #run it here
        #    return "pass"
        else:
            unknown_engine = True
    except Exception as e:
        # return error object
        error_str = safe_md_string(e)
        print(error_str, file=sys.__stdout__)

    if unknown_engine:
        raise RuntimeError(f"unknown engine {engine}")

    for tag in error_categories[engine]:
        if re.search(error_categories[engine][tag], error_str):
            return [tag, f"```{error_str}```"]

    return ["other", f"```{error_str}```"]


@dataclass
class SuppressOutput:
    """
    redirect stdout and/or stderr to os.devnull
    stdout: whether to suppress stdout
    stderr: whether to suppress stderr
    """

    stdout: bool = False
    stderr: bool = False

    def suppress(self):
        "begin to suppress output(s)"
        if self.stdout:
            self.orig_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")
        if self.stderr:
            self.orig_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")

    def restore(self):
        "restore output(s)"
        if self.stdout:
            sys.stdout.close()
            sys.stdout = self.orig_stdout
        if self.stderr:
            sys.stderr.close()
            sys.stderr = self.orig_stderr


class RequestCache:
    """
    caching is used to prevent the need to download the same responses from the remote server multiple times during testing
    currently no handling of unexpected cache misses
    """

    def __init__(self, mode="off", direc="cache"):
        """
        mode:
            "off" to disable caching (does not wipe any existing cache data)
            "store" to wipe and store fresh results in the cache
            "reuse" to only use existing cache files
            "auto" to download only if missing
            could also implement "auto" mode that only downloads on a cache miss
        direc: the directory used to store the cache
        """
        self.mode = mode

        # store absolute cache dir path to ensure it is found regardless of current directory
        self.absolute_dir = os.path.join(os.getcwd(), direc)

        if mode == "store":
            self.wipe()

    def wipe(self):
        "wipe any existing cache directory and setup a new empty one"

        shutil.rmtree(self.absolute_dir, ignore_errors=True)
        os.makedirs(self.absolute_dir, exist_ok=True)

    def get_path(self, request=None):
        """
        return path to cached request response
        or just the cache base directory for a null request
        """

        return os.path.join(
            f"{self.absolute_dir}", hashlib.sha256(request.encode("UTF-8")).hexdigest()
        )
        # return f"{self.absolute_dir}/{hashlib.sha256(request.encode('UTF-8')).hexdigest()}"

    def get_entry(self, request):
        """
        load cached response
        note this should only be used in a context where you trust the integrity of the cache files
        due to using pickle
        note also: no explicit handling of cache misses yet implemented
        """

        with open(self.get_path(request), "rb") as f:
            return pickle.load(f)

    def set_entry(self, request, response):
        """
        save a response to the cache
        """

        with open(self.get_path(request), "wb") as fout:
            pickle.dump(response, fout)

    def do_request(self, request):
        """
        automatically handle the cache operations for the call_back function
        """

        if self.mode == "reuse" or (
            self.mode == "auto" and os.path.isfile(self.get_path(request))
        ):
            return self.get_entry(request)

        response = requests.get(request)
        response.raise_for_status()

        if self.mode == "store" or self.mode == "auto":
            self.set_entry(request, response)
        return response


class MarkdownTable:
    """
    helper class to accumulate rows of data with a header and optional summary row
    to be written to file as a markdown table
    """

    def __init__(
        self, labels: str, keys: str, splitter="|", PASS="pass", FAIL="FAIL", NA="NA"
    ):
        "specify column headers and variable names"
        self.labels = [x.strip() for x in labels.split(splitter)]
        self.keys = [x.strip() for x in keys.split(splitter)]
        assert len(self.keys) == len(self.labels)
        self.data = {key: [] for key in self.keys}
        self.summary = None
        self.PASS = PASS
        self.FAIL = FAIL
        self.NA = NA

    def __getitem__(self, key):
        "get last row of named column"
        assert key in self.keys
        assert len(self.data[key]) > 0
        return self.data[key][-1]

    def __setitem__(self, key, value):
        "set (ie overwrite) last row of named column"
        assert key in self.keys
        assert len(self.data[key]) > 0
        self.data[key][-1] = value

    def new_row(self, vars={}):
        "ingest the next row from a variables dict (eg locals())"
        for key in self.keys:
            if key not in vars:
                self.data[key].append(self.NA)
            else:
                self.data[key].append(vars[key])

    def update_row(self, vars):
        "update the last row from a variables dict (eg locals())"
        for key in self.keys:
            if key not in vars:
                self.data[key][-1] = self.NA
            else:
                self.data[key][-1] = vars[key]

    def n_rows(self):
        "return number of data rows"
        return len(self.data[self.keys[0]])

    def n_cols(self):
        "return number of data columns"
        return len(self.data)

    def add_summary(self, key, value):
        "fill in the optional summary cell for the named column"
        if not self.summary:
            self.summary = {key: "" for key in self.keys}

        self.summary[key] = value

    def add_count(self, key, func, format="n={count}"):
        "add a basic summary counting how many times the function is true"
        count = len([x for x in self.data[key] if func(x)])

        self.add_summary(key, format.format(count=count))

    def regex_summary(self, key, patterns, format="{summary}", func=None):
        """
        count how many cells match each pattern
        transform cell contents with optional callback function
        """
        counts = defaultdict(int)

        for i, cell in enumerate(self.data[key]):
            if type(cell) is list:
                value = str(cell[0])
            else:
                value = str(cell)

            match = None
            for regex, tag in patterns.items():
                if re.search(regex, value):
                    match = tag
                    break
            if not match:
                match = "other"
            counts[match] += 1

            if func:
                self.data[key][i] = func(key, self.data[key][i], match)

        summary = " ".join([f"n_{tag}={counts[tag]}" for tag in counts])
        self.add_summary(key, format.format(summary=summary))

    def make_fold(self, summary, details, quote=False):
        "make foldable/hideable html cell"
        if quote:
            format = "<details><summary>{summary}</summary>```{details}```</details>"
        else:
            format = "<details><summary>{summary}</summary>{details}</details>"

        return format.format(summary=summary, details=details)

    def generate_summary(self, counts):
        "generate the summary cell contents"

        total = sum([counts[tag] for tag in counts])
        summary = []
        fails = total

        if self.PASS in counts:
            summary.append(f"pass={counts[self.PASS]}")
            fails -= counts[self.PASS]
            del counts[self.PASS]
        if self.NA in counts:
            summary.append(f"NA={counts[self.NA]}")
            fails -= counts[self.NA]
            del counts[self.NA]

        if len(counts) > 1:
            # more than one error category, make folded details
            summary.append(f"FAIL={fails}")  # summary has total fails
            summary = " ".join(summary)
            details = " ".join(
                [f"n_{tag}={counts[tag]}" for tag in counts]
            )  # give failures breakdown

            final = self.make_fold(summary, details)
        else:
            # only one error category at most, use only a summary
            if len(counts) == 1:
                tag = list(counts)[0]
                summary.append(f"{tag}={counts[tag]}")

            final = summary = " ".join(summary)

        return final

    def simple_summary(self, key):
        "count how many cells contain each distinct value"
        counts = defaultdict(int)
        for cell in self.data[key]:
            if type(cell) is list:
                tag = str(cell[0])
            else:
                tag = str(cell)

            counts[tag] += 1

        self.add_summary(key, self.generate_summary(counts))

    def format_cell(self, cell):
        """
        produce the final fully formatted markdown table cell contents
        """

        if type(cell) is list:
            assert len(cell) == 2
            details = safe_md_string(cell[1])
            return self.make_fold(cell[0], details)

        return str(cell)

    def transform_column(self, key, func=None):
        "pass all column values through a function"
        for i in range(len(self.data[key])):
            if func:
                self.data[key][i] = func(self.data[key][i])
            else:
                self.data[key][i] = self.format_cell(self.data[key][i])

    def print_last_row(self):
        if self.n_rows() == 0:
            print("-")
            return
        print(" ".join([str(self.data[key][-1]) for key in self.data]))

    def print_col_lengths(self):
        print(" ".join([str(len(self.data[key])) for key in self.data]))

    def write(self, fout, sep="|", end="\n"):
        "write the markdown table to file"
        fout.write(sep + sep.join(self.labels) + sep + end)
        fout.write(sep + sep.join(["---" for x in self.labels]) + sep + end)
        if self.summary:
            fout.write(
                sep
                + sep.join([str(self.summary[key]) for key in self.keys])
                + sep
                + end
            )

        for i in range(self.n_rows()):
            fout.write(
                sep
                + sep.join([str(self.data[key][i]) for key in self.keys])
                + sep
                + end
            )

    def process_engine_outcomes(self, engine, key):
        """
        process a column containing engine test outcomes/error messages
        categorise errors and generate summary counts
        """

        # dict to record frequency of each engine error type
        errors = {"other": 0}
        for pattern, error_tag in error_categories[engine].items():
            errors[error_tag] = 0

        for i in range(len(self.data[key])):
            if not self.data[key][i]:
                self.data[key][i] = "pass"
                continue

            # make sure the error message will not break the markdown table
            error_str = safe_md_string(self.data[key][i])

            # category match the error message
            cell_text = None
            for pattern in error_categories[engine]:
                if re.search(pattern, error_str):
                    error_tag = error_categories[engine][pattern]
                    errors[error_tag] += 1
                    cell_text = self.make_fold(
                        "FAIL ({error_tag})", error_str, quote=True
                    )
                    break

            if not cell_text:
                errors["other"] += 1
                cell_text = self.make_fold("FAIL (other)", error_str, quote=True)

            self.data[key][i] = cell_text

        # generate summary counts by error category
        total_errors = sum([count for _, count in errors.items()])
        details = " ".join(
            [f"{error_tag}={count}" for error_tag, count in errors.items()]
        )
        summary_text = self.make_fold(f"fails={total_errors}", details)
        self.add_summary(key, summary_text)


def safe_md_string(value):
    """
    make a string safe to insert into markdown table
    """

    return (
        str(value)
        .replace("\n", " ")
        .replace("\r", "")
        .replace("\t", " ")
        .replace("   ", " ")
        .replace("  ", " ")
        .replace("|", "<br>")
        .replace("`", " ")
    )


def download_file_from_link(
    engine, download_link, output_file="results.zip", max_wait_time=600, wait_time=2
):
    """
    Function to download a file from a given URL.

    Parameters:
    download_link (str): The URL of the file to download.
    output_file (str): The name of the file to save the download as. Defaults to 'results.zip'.
    max_wait_time (int): The maximum time to wait for the file to be ready to download. Defaults to 300 seconds.
    wait_time (int): The time to wait between checks if the file is ready to download. Defaults to 2 seconds.

    Returns:
    bool: True if the file was downloaded successfully, False otherwise.
    """

    start_time = time.time()

    while True:
        response = requests.get(download_link)
        if response.status_code != 404 or time.time() - start_time > max_wait_time:
            break
        time.sleep(wait_time)

    if response.status_code == 200:
        print(f"Downloading {engine} results...")
        with requests.get(download_link, stream=True) as r:
            with open(output_file, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        filepath = os.path.abspath(output_file)
        return filepath
    else:
        print(f"Failed to download {engine} results.")
        raise HTTPError(f"Failed to download {engine} results.")


def create_results_table(results, sbml_filepath, sedml_filepath, output_dir):
    """
    Create a markdown table of the results.

    Input: results, TYPES, sbml_filepath, sedml_filepath, ENGINES, output_dir
    Output: results_md_table

    """

    pass_html = "&#9989; PASS"
    fail_html = "&#10060; FAIL"
    warning_html = "&#9888; WARNING"
    unsure_html = "&#10067; UNSURE"
    xfail_html = "&#9888; XFAIL"

    links = ["view", "download", "logs"]
    for e in results.keys():
        results[e].update(process_log_yml_dict(results[e]["log_yml"]))
        if "detailed_error_log" in results[e].keys():
            if results[e]["detailed_error_log"] != {}:
                results[e]["status"] = results[e]["detailed_error_log"]["status"]
                results[e]["error_message"] = results[e]["detailed_error_log"][
                    "error_message"
                ]
        if any([link in results[e].keys() for link in links]):
            results[e]["links"] = "<br>".join(
                [
                    f"{create_hyperlink(results[e][k], title=k)}"
                    for k in results[e].keys()
                    if k in links
                ]
            )
        results[e]["name"] = ENGINES[e]["name"]

    results_table = pd.DataFrame.from_dict(results).T
    results_table.rename(
        columns={"status": PASS_FAIL, "error_message": ERROR, "exception_type": TYPE},
        inplace=True,
    )

    results_table.index.name = ENGINE
    results_table.reset_index(inplace=True)

    # Error
    results_table[ERROR] = results_table.apply(
        lambda x: None if x[PASS_FAIL] == x[ERROR] else x[ERROR], axis=1
    )
    results_table[ERROR] = results_table[ERROR].apply(lambda x: ansi_to_html(x))

    results_table[PASS_FAIL] = results_table[PASS_FAIL].apply(
        lambda x: f"{fail_html}"
        if x == "FAIL"
        else f"{pass_html}"
        if x == "pass"
        else f"{warning_html}"
        if x == "WARNING"
        else x
    )

    # d1 plot clickable link
    results_table[D1] = results_table[ENGINE].apply(
        lambda x: d1_plots_dict(output_dir).get(x, None)
    )
    results_table[D1] = results_table[D1].apply(
        lambda x: create_hyperlink(x, title="plot")
    )

    for e in ENGINES.keys():
        compatibility_content = check_file_compatibility_test(
            e, sbml_filepath, sedml_filepath
        )
        if compatibility_content[0] == "pass":
            results_table.loc[results_table[ENGINE] == e, COMPAT] = collapsible_content(
                compatibility_content[1], title=f"{pass_html}"
            )
        elif compatibility_content[0] == "unsure":
            results_table.loc[results_table[ENGINE] == e, COMPAT] = collapsible_content(
                compatibility_content[1], title=f"{unsure_html}"
            )
        else:
            results_table.loc[results_table[ENGINE] == e, COMPAT] = collapsible_content(
                compatibility_content[1], title=f"{fail_html}"
            )

    # add xfail to engines that do not support sbml
    sbml_incompatible_ENGINES = [
        e for e in ENGINES.keys() if "sbml" not in ENGINES[e]["formats"][0]
    ]
    for e in sbml_incompatible_ENGINES:
        engine_name = ENGINES[e]["name"]
        unique_compatible_filetpyes_strings = ", ".join(
            [TYPES[i] for i in ENGINES[e]["formats"][0] if i in list(TYPES.keys())]
        )
        compatibility = f"Only {unique_compatible_filetpyes_strings} are compatible with {engine_name}."
        compatibility_content = f"EXPECTED FAIL<br><br>{compatibility}"
        results_table.loc[results_table[ENGINE] == e, COMPAT] = collapsible_content(
            compatibility_content, title=f"{xfail_html}"
        )
        results_table.loc[results_table[ENGINE] == e, PASS_FAIL] = f"{xfail_html}"

    for e in results_table[ENGINE]:
        links = ""
        error_message = ""
        error_type = ""
        expected_fail = ""

        if (
            results_table.loc[results_table[ENGINE] == e, PASS_FAIL].values[0]
            == "{xfail_html}"
        ):
            expected_fail = "EXPECTED FAIL<br><br>"
        if len(results_table.loc[results_table[ENGINE] == e, ERROR].values[0]) > 1:
            error_message = f"ERROR MESSAGE:<br>{results_table.loc[results_table[ENGINE] == e, ERROR].values[0]}<br><br>"
        if "links" in results_table.columns:
            links = results_table.loc[results_table[ENGINE] == e, "links"].values[0]
            links = f"{links}<br><br>"
        if TYPE in results_table.columns:
            if len(results_table.loc[results_table[ENGINE] == e, TYPE].values[0]) > 1:
                error_type = f"ERROR TYPE:<br>{results_table.loc[results_table[ENGINE] == e, TYPE].values[0]}"

        links_error = f"{expected_fail}{links}{error_message}{error_type}"
        results_table.loc[results_table[ENGINE] == e, "links_error"] = links_error

    # add links as collapsible content to pass / fail column
    for e in results_table[ENGINE]:
        title = results_table.loc[results_table[ENGINE] == e, PASS_FAIL].values[0]
        content = results_table.loc[results_table[ENGINE] == e, "links_error"].values[0]
        results_table.loc[results_table[ENGINE] == e, PASS_FAIL] = collapsible_content(
            content, title
        )
        results_table.loc[results_table[ENGINE] == e, "name"] = collapsible_content(
            content=f'{ENGINES[e]["url"]}<br>{ENGINES[e]["status"]}',
            title=f'{ENGINES[e]["name"]}',
        )

    return results_table


def process_log_yml_dict(log_yml_dict):
    status = ""
    error_message = ""
    exception_type = ""

    if log_yml_dict == {}:
        return {
            "status": "FAIL",
            "error_message": "Error unknown. The log.yml containing error information was not found.",
            "exception_type": "",
        }

    log_yml_str = str(log_yml_dict)
    if log_yml_dict["status"] == "SUCCEEDED":
        status = "pass"
        # to deal with cases like amici where the d1 plot max x is half the expected value
        pattern_max_number_of_steps = (
            "simulation failed: Reached maximum number of steps"
        )
        pattern_match = re.search(pattern_max_number_of_steps, log_yml_str)
        if pattern_match:
            status = "FAIL"
            error_message = "Reached maximum number of steps"
    elif log_yml_dict["status"] == "FAILED":
        status = "FAIL"
        exception = log_yml_dict["exception"]
        error_message = exception["message"]
        exception_type = exception["type"]
    # in the case of vcell the status is QUEUED
    elif log_yml_dict["status"] == "QUEUED":
        status = "FAIL"
        error_message = "status: QUEUED"
    else:
        status = None

    return {
        "status": status,
        "error_message": error_message,
        "exception_type": exception_type,
    }


def run_biosimulators_remotely(
    engine_keys,
    sedml_file_name,
    sbml_file_name,
    d1_plots_remote_dir,
    test_folder="tests",
):
    """run with directory pointing towards the location of the sedml and sbml files"""

    engines = {k: v for k, v in ENGINES.items() if k in engine_keys}

    remote_output_dir = "remote_results"
    remote_output_dir = os.path.join(test_folder, remote_output_dir)

    results_remote = dict()
    for e in engines.keys():
        results_remote[e] = run_biosimulators_remote(e, sedml_file_name, sbml_file_name)

    extract_dir_dict = dict()
    for e, link in results_remote.items():
        try:
            extract_dir = get_remote_results(e, link["download"], remote_output_dir)
        except Exception as emessage:
            print(f"Error downloading {e} results: {emessage}")
            continue
        extract_dir_dict[e] = extract_dir

    for e, extract_dir in extract_dir_dict.items():
        log_yml_path = find_file_in_dir("log.yml", extract_dir)[0]
        with open(log_yml_path) as f:
            log_yml_dict = yaml.safe_load(f)
        results_remote[e]["log_yml"] = log_yml_dict

    file_paths = find_files(remote_output_dir, ".pdf")
    move_d1_files(file_paths, d1_plots_remote_dir)

    # remove the remote results directory
    if os.path.exists(remote_output_dir):
        shutil.rmtree(remote_output_dir)
        print("Removed " + remote_output_dir + " folder")

    return results_remote


def run_biosimulators_locally(
    engine_keys,
    sedml_file_name,
    sbml_file_name,
    d1_plots_local_dir,
    test_folder="tests",
):
    engines = {k: v for k, v in ENGINES.items() if k in engine_keys}
    results_local = {}

    output_folder = "local_results"
    local_output_dir = os.path.join(test_folder, output_folder)

    for e in engines.keys():
        print("Running " + e)
        local_output_dir_e = os.path.abspath(os.path.join(local_output_dir, e))
        print(local_output_dir_e)
        results_local[e] = run_biosimulators_docker(
            e, sedml_file_name, sbml_file_name, output_dir=local_output_dir_e
        )

    file_paths = find_files(local_output_dir, ".pdf")
    print("file paths:", file_paths)
    move_d1_files(file_paths, d1_plots_local_dir)

    # if it exists remove the output folder
    if os.path.exists(local_output_dir):
        shutil.rmtree(local_output_dir)
        print("Removed " + local_output_dir + " folder")

    return results_local


def create_combined_results_table(
    results_remote,
    results_local,
    sedml_file_name,
    sbml_file_name,
    d1_plots_local_dir,
    d1_plots_remote_dir,
    test_folder="tests",
):
    suffix_remote = " (R)"
    suffix_local = " (L)"

    # save results_remote and results_local as json files with dicts
    path_to_results_remote = os.path.join(test_folder, "results_remote.json")
    path_to_results_local = os.path.join(test_folder, "results_local.json")

    with open(path_to_results_remote, "w") as f:
        json.dump(results_remote, f, indent=4)
    with open(path_to_results_local, "w") as f:
        json.dump(results_local, f, indent=4)

    # Create results tables for remote and local results
    results_table_remote = create_results_table(
        results_remote, sbml_file_name, sedml_file_name, d1_plots_remote_dir
    )
    results_table_local = create_results_table(
        results_local, sbml_file_name, sedml_file_name, d1_plots_local_dir
    )

    shared_columns = [ENGINE, COMPAT, "name"]
    results_table_remote.columns = [
        f"{col}{suffix_remote}" if col not in shared_columns else col
        for col in results_table_remote.columns
    ]
    results_table_local.columns = [
        f"{col}{suffix_local}" if col not in shared_columns else col
        for col in results_table_local.columns
    ]

    combined_results = pd.merge(
        results_table_remote, results_table_local, on=shared_columns, how="outer"
    )
    combined_results = combined_results.reindex(
        columns=[ENGINE] + sorted(combined_results.columns[1:])
    )
    combined_results = combined_results.drop(columns=[ENGINE]).rename(
        columns={"name": ENGINE}
    )

    # Define the order of columns
    cols_order = [
        ENGINE,
        COMPAT,
        f"{PASS_FAIL}{suffix_remote}",
        f"{PASS_FAIL}{suffix_local}",
        f"{D1}{suffix_remote}",
        f"{D1}{suffix_local}",
    ]

    combined_results = combined_results[cols_order]

    # Save the results to a Markdown file with utf-8 encoding
    path_to_results = os.path.join(
        test_folder, f"results_{sedml_file_name.split('.')[0].replace(' ', '')}.md"
    )
    print("Saving results to:", path_to_results)
    with open(path_to_results, "w", encoding="utf-8") as f:
        f.write(combined_results.to_markdown(index=False))

    print("Number of columns in md table:", len(combined_results.columns))
    print("Number of rows in md table:", len(combined_results))
    print(combined_results.head())

    return combined_results


def run_biosimulators_remotely_and_locally(
    engine_keys,
    sedml_file_name,
    sbml_file_name,
    d1_plots_remote_dir,
    d1_plots_local_dir,
    test_folder="tests",
):
    results_remote = run_biosimulators_remotely(
        engine_keys,
        sedml_file_name=sedml_file_name,
        sbml_file_name=sbml_file_name,
        d1_plots_remote_dir=d1_plots_remote_dir,
        test_folder=test_folder,
    )

    results_local = run_biosimulators_locally(
        engine_keys,
        sedml_file_name=sedml_file_name,
        sbml_file_name=sbml_file_name,
        d1_plots_local_dir=d1_plots_local_dir,
        test_folder=test_folder,
    )

    results_table = create_combined_results_table(
        results_remote,
        results_local,
        sedml_file_name=sedml_file_name,
        sbml_file_name=sbml_file_name,
        d1_plots_local_dir=d1_plots_local_dir,
        d1_plots_remote_dir=d1_plots_remote_dir,
        test_folder=test_folder,
    )

    return results_table
