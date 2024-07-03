#!/bin/bash

#
# test that the results.md file can be regenerated
#

set -ex

# Install if missing locally
# sudo apt-get install wget unzip --fix-missing --yes

#download and extract test suite files in not already present
if [[ ! -f semantic_tests_with_sedml_and_graphs.v3.4.0.zip ]] ; then
    wget --quiet https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip
fi

if [[ ! -d semantic ]] ; then
    unzip -qq semantic_tests_with_sedml_and_graphs.v3.4.0.zip
fi

#run the tests, output markdown table with summary
./process_test_suite.py --suite-path ./semantic --sbml-level_version 'sbml-l3v2' --output-file ./results.md
