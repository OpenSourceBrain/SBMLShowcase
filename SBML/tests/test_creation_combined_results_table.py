import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))) # to import utils
import utils
import argparse

engines = utils.ENGINES

# Save the current working directory
cwd = os.getcwd()
print('Current working directory:', cwd)

# SBML folder is one folder up relative to cwd
path_to_sbml_folder = os.path.abspath(os.path.join(cwd, os.pardir))
print('Path to SBML folder:', path_to_sbml_folder)

# change the working directory to the SBML folder (because here the SBML and SED-ML files are located)
os.chdir(path_to_sbml_folder)
print('Changed working directory to:', os.getcwd())

sbml_file_name = 'LEMS_NML2_Ex9_FN.sbml'
sedml_file_name = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing

# output_dir is set to 'd1_plots' by default but can be changed using the --output-dir argument (required to deal with GitHub Actions permission issues)
parser = argparse.ArgumentParser(description='Test compatibility of different biosimulation engines')
parser.add_argument('--output-dir',action='store',default='d1_plots',help='prefix of the output directory where the d1 plots will be saved')
args = parser.parse_args()

test_folder = 'tests'

d1_plots_local_dir = os.path.join(test_folder, args.output_dir + '_local')
d1_plots_remote_dir = os.path.join(test_folder, args.output_dir + '_remote')

results_local = {'amici': 'pass', 'brian2': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/brian2' returned non-zero exit status 1```"], 'bionetgen': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/bionetgen' returned non-zero exit status 1```"], 'boolnet': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/boolnet' returned non-zero exit status 1```"], 'cbmpy': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/cbmpy' returned non-zero exit status 1```"], 'cobrapy': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/cobrapy' returned non-zero exit status 1```"], 'copasi': 'pass', 'gillespy2': 'pass', 'ginsim': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/ginsim' returned non-zero exit status 1```"], 'libsbmlsim': 'pass', 'masspy': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/masspy' returned non-zero exit status 1```"], 'netpyne': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/netpyne' returned non-zero exit status 1```"], 'neuron': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/neuron' returned non-zero exit status 1```"], 'opencor': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/opencor' returned non-zero exit status 1```"], 'pyneuroml': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/pyneuroml' returned non-zero exit status 1```"], 'pysces': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/pysces' returned non-zero exit status 1```"], 'rbapy': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/rbapy' returned non-zero exit status 1```"], 'smoldyn': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/smoldyn' returned non-zero exit status 1```"], 'tellurium': 'pass', 'vcell': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/vcell' returned non-zero exit status 1```"], 'xpp': ['other', "```Command '-i /root/in/LEMS_NML2_Ex9_FN_missing_xmlns.omex -o /root/out' in image 'ghcr.io/biosimulators/xpp' returned non-zero exit status 1```"]}
results_remote = {'amici': ['pass', '', ''], 'brian2': ['FAIL', "No module named 'libsbml'", 'ModuleNotFoundError'], 'bionetgen': ['FAIL', 'The COMBINE/OMEX did not execute successfully:\n\n  The SED document did not execute successfully:\n  \n    Language for model `net1` is not supported.\n      - Model language `urn:sedml:language:sbml` is not supported. Models must be in BNGL format (e.g., `sed:model/@language` must match `^urn:sedml:language:bngl(\\.|$)` such as `urn:sedml:language:bngl`).', 'CombineArchiveExecutionError'], 'boolnet': ['FAIL', 'The COMBINE/OMEX did not execute successfully:\n\n  The SED document did not execute successfully:\n  \n    Simulation `sim1` is invalid.\n      - Number of points (20000) must be equal to the difference between the output end (200.0) and start times (0.0).', 'CombineArchiveExecutionError'], 'cbmpy': ['FAIL', 'The COMBINE/OMEX did not execute successfully:\n\n  The SED document did not execute successfully:\n  \n    UniformTimeCourseSimulation `sim1` is not supported.\n      - Simulation sim1 of type `UniformTimeCourseSimulation` is not supported. Simulation must be an instance of one of the following:\n          - SteadyStateSimulation', 'CombineArchiveExecutionError'], 'cobrapy': ['FAIL', 'The COMBINE/OMEX did not execute successfully:\n\n  The SED document did not execute successfully:\n  \n    UniformTimeCourseSimulation `sim1` is not supported.\n      - Simulation sim1 of type `UniformTimeCourseSimulation` is not supported. Simulation must be an instance of one of the following:\n          - SteadyStateSimulation', 'CombineArchiveExecutionError'], 'copasi': ['pass', '', ''], 'gillespy2': ['pass', '', ''], 'ginsim': ['FAIL', 'The COMBINE/OMEX did not execute successfully:\n\n  The SED document did not execute successfully:\n  \n    Simulation `sim1` is invalid.\n      - The interval between the output start and time time must be an integer multiple of the number of steps, not `0.01`:\n          Output start time: 0.0\n          Output end time: 200.0\n          Number of steps: 20000', 'CombineArchiveExecutionError'], 'libsbmlsim': ['pass', '', ''], 'masspy': ['FAIL', 'The COMBINE/OMEX did not execute successfully:\n\n  The SED document did not execute successfully:\n  \n    Something went wrong reading the SBML model. Most likely the SBML model is not valid. Please check that your model is valid using the `mass.io.sbml.validate_sbml_model` function or via the online validator at http://sbml.org/validator .\n    \t`(model, errors) = validate_sbml_model(filename)`\n    If the model is valid and cannot be read please open an issue at https://github.com/SBRG/masspy/issues .', 'CombineArchiveExecutionError'], 'netpyne': ['FAIL', "No module named 'libsbml'", 'ModuleNotFoundError'], 'neuron': ['FAIL', "No module named 'libsbml'", 'ModuleNotFoundError'], 'opencor': ['FAIL', "No module named 'libsbml'", 'ModuleNotFoundError'], 'pyneuroml': ['FAIL', "No module named 'libsbml'", 'ModuleNotFoundError'], 'pysces': ['FAIL', 'The COMBINE/OMEX did not execute successfully:\n\n  The SED document did not execute successfully:\n  \n    Model at /tmp/tmp1bq_quiv/./LEMS_NML2_Ex9_FN.sbml could not be imported:\n      \n      File /tmp/tmp1bq_quiv/./LEMS_NML2_Ex9_FN.sbml.xml does not exist', 'CombineArchiveExecutionError'], 'rbapy': ['FAIL', 'The COMBINE/OMEX did not execute successfully:\n\n  The SED document did not execute successfully:\n  \n    Language for model `net1` is not supported.\n      - Model language `urn:sedml:language:sbml` is not supported. Models must be in RBA format (e.g., `sed:model/@language` must match `^urn:sedml:language:rba(\\.|$)` such as `urn:sedml:language:rba`).', 'CombineArchiveExecutionError'], 'smoldyn': ['FAIL', "No module named 'libsbml'", 'ModuleNotFoundError'], 'tellurium': ['pass', '', ''], 'vcell': [None, '', ''], 'xpp': ['FAIL', "No module named 'libsbml'", 'ModuleNotFoundError']}

results_table = utils.create_combined_results_table(results_remote, 
                                  results_local, 
                                  sedml_file_name, 
                                  sbml_file_name, 
                                  d1_plots_local_dir, 
                                  d1_plots_remote_dir,
                                  test_folder='tests')

print(results_table)
    