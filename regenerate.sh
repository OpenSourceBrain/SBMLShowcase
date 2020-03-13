#!/bin/bash

set -e

cd SBML

jnml -sbml-import BIOMD0000000184.xml 1000 0.01
jnml -sbml-import BIOMD0000000127_url.xml  140 0.01
mv BIOMD00000*_LEMS.xml ../LEMS

cd ../LEMS

jnml BIOMD0000000184_LEMS.xml -brian
mv BIOMD0000000184_LEMS_brian.py ../Brian
jnml BIOMD0000000184_LEMS.xml -brian2
mv BIOMD0000000184_LEMS_brian2.py ../Brian


jnml BIOMD0000000184_LEMS.xml -neuron
mv BIOMD0000000184_LEMS_nrn.py Lavrentovich2008_Ca_Oscillations_0.mod ../NEURON

cd ../NeuroML2

jnml LEMS_NML2_Ex9_FN.xml -sbml-sedml
mv *sedml ../SBML
mv *sbml ../SBML