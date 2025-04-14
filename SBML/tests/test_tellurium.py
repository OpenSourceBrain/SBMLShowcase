import os
import sys

import tellurium as te

te.setDefaultPlottingEngine("matplotlib")

path_to_sbml_folder = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# change the working directory to the SBML folder
os.chdir(path_to_sbml_folder)
print("Changed working directory to:", os.getcwd())

sedml_file = "LEMS_NML2_Ex9_FN.sedml"
if len(sys.argv) > 1:
    sedml_file = sys.argv[1]

# For technical reasons, any software which uses libSEDML
# must provide a custom build - Tellurium uses tesedml
try:
    import libsedml
except ImportError:
    import tesedml as libsedml
sedml_doc = libsedml.readSedML(sedml_file)
n_errors = sedml_doc.getErrorLog().getNumFailsWithSeverity(libsedml.LIBSEDML_SEV_ERROR)
print("Read SED-ML file %s, number of errors: %i" % (sedml_file, n_errors))
if n_errors > 0:
    print(sedml_doc.getErrorLog().toString())

print(sedml_doc)

print(dir(sedml_doc))
print(sedml_doc.toSed())

createOutputs = "-nogui" not in sys.argv

# execute SED-ML using Tellurium
te.executeSEDML(
    sedml_doc.toSed(),
    workingDir=".",
    saveOutputs=True,
    outputDir=".",
    createOutputs=createOutputs,
)
