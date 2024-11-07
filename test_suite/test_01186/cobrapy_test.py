import cobra
from cobra.io import load_json_model, save_json_model, load_matlab_model, save_matlab_model, read_sbml_model, write_sbml_model

import os

starting_dir = os.getcwd()
files = os.listdir(starting_dir)
sbml_file = [f for f in files if f.endswith('.xml') and 'sedml' not in f and 'sbml' in f][0]

print(sbml_file)

# read model
model = read_sbml_model(sbml_file)
model_validated, errors = cobra.io.sbml.validate_sbml_model(sbml_file)

print(model_validated)

print("")
print("Errors:")
print(errors)