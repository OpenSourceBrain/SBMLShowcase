#!/bin/bash

set -e

cd SBML

jnml -sbml-import BIOMD0000000184.xml 1000 0.01
mv BIOMD0000000184_LEMS.xml ../LEMS

