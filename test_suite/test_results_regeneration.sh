#!/bin/bash

#
# test that the results.md file can be regenerated
#

set -ex

# Install wget and unzip if missing locally, eg for ubuntu/debian systems:
#   sudo apt-get install wget unzip --fix-missing --yes

# Uncomment the wget and unzip commands if you don't already have the zip file downloaded
wget https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip
unzip semantic_tests_with_sedml_and_graphs.v3.4.0.zip

./process_test_suite.py --suite-path ./semantic --suite-glob '*/*-sbml-l3v2.xml' --output-file ./results.md \
                        --limit 400 --engine-errors 2> errors.log > output.log
