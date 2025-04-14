#!/bin/bash
set -ex

### A script to test various combinations of import/export of SBML to/from NeuroML2 & LEMS

## Test converting SBML to LEMS
cd SBML
pynml -sbml-import BIOMD0000000184.xml 1000 0.01
pynml -sbml-import BIOMD0000000127_url.xml  140 0.01
mv BIOMD00000*_LEMS.xml ../LEMS


## Test executing generated LEMS with pyNeuroML
cd ../LEMS
pynml BIOMD0000000184_LEMS.xml -nogui


## Test converting generated LEMS to Brian simulator code
pynml BIOMD0000000184_LEMS.xml -brian
mv BIOMD0000000184_LEMS_brian.py ../Brian
pynml BIOMD0000000184_LEMS.xml -brian2
mv BIOMD0000000184_LEMS_brian2.py ../Brian


## Test converting generated LEMS to NEURON simulator code
pynml BIOMD0000000184_LEMS.xml -neuron -run -nogui
mv BIOMD0000000184_LEMS_nrn.py Lavrentovich2008_Ca_Oscillations_0.mod ../NEURON


## Test converting a NeuroML+LEMS model to SBML+SED-ML
cd ../NeuroML2
pynml LEMS_NML2_Ex9_FN.xml -sbml-sedml
pynml LEMS_Regular_HindmarshRose.xml -sbml-sedml
mv *sedml ../SBML
mv *sbml ../SBML

cd ../SBML/tests
./validateAll.sh
python test_tellurium.py LEMS_Regular_HindmarshRose.sedml -nogui
python test_tellurium.py LEMS_NML2_Ex9_FN.sedml -nogui

echo "Finished all tests!"
