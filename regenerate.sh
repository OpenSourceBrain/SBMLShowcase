#!/bin/bash

set -e

cd SBML

jnml -sbml-import BIOMD0000000184.xml 1000 0.01
mv BIOMD0000000184_LEMS.xml ../LEMS

cd ../LEMS

jnml BIOMD0000000184_LEMS.xml -brian
mv BIOMD0000000184_LEMS_brian.py ../Brian
jnml BIOMD0000000184_LEMS.xml -brian2
mv BIOMD0000000184_LEMS_brian2.py ../Brian

