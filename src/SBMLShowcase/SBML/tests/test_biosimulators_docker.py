#!/usr/bin/env python

"""
use pymetadata module to create a minimal valid combine archive
using LEMS_NML2_Ex9_FN.sbml and LEMS_NML2_Ex9_FN.sedml
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import utils

cwd = os.getcwd()
print("Current working directory:", cwd)
path_to_sbml_folder = os.path.abspath(os.path.join(cwd, os.pardir))
print("Path to SBML folder:", path_to_sbml_folder)
os.chdir(path_to_sbml_folder)
print("Changed working directory to:", os.getcwd())

sbml_file_name = "LEMS_NML2_Ex9_FN.sbml"
# sedml_filepath = 'LEMS_NML2_Ex9_FN.sedml' #xmlns:sbml added manually
sedml_file_name = "LEMS_NML2_Ex9_FN_missing_xmlns.sedml"  # xmlns:sbml missing

omex_filepath = utils.create_omex(sedml_file_name, sbml_file_name)

print("Testing biosimulators-core (tellurium)")
message = utils.biosimulators_core("tellurium", omex_filepath)
print("..................")
print(message)
print("Finished")
