#!/bin/bash
set -ex

### A script to validate SBML & SED-ML files using pyNeuroML

# change directory to one folder up
cd ..

pynml -validate-sbml *.sbml

echo "All SBML files valid"

pynml -validate-sbml *.xml

echo "All XML files are valid SBML"

pynml -validate-sedml *.sedml

echo "All SEDML files are valid"
