#!/bin/bash
set -ex

### A script to validate SBML (& SED-ML) files using pyNeuroML

pynml -validate-sbml LEMS_NML2_Ex9_FN.sbml

pynml -validate-sbml Run_Regular_HindmarshRose.sbml
