# Tabulates results of validation tests on SBML test suite

The `process_test_suite.py` script currently runs three tests from pyneuroml on all SBML files that match the input glob argument given to it: validate SBML, validate SBML (with strict unit checks), validate SEDML. The SEDML file is assumed to have the same name as the SBML file except the `.xml` extension must to changed to `-sedml.xml`. The output is a markdown file containing a simple table of the results obtained on each file, where each test results is recorded as either a pass (True) or fail (False)

- First download the [zipfile](https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip) (or the latest equivalent) of the [SBML test suite](https://github.com/sbmlteam/sbml-test-suite) that includes [SEDML](https://github.com/SED-ML/sed-ml) files.

- Extract to any convenient location, for example using the `unzip` command:

```
unzip semantic_tests_with_sedml_and_graphs.v3.4.0.zip
```

- Then run the `process_test_suite.py` tool, pointing it towards the extracted test files, for example if the extraction folder is at `/home/vagrant/test_suite_files/semantic` and the `process_test_suite.py` script is in the current directory:

```
./process_test_suite.py --suite-path /home/vagrant/test_suite_files/semantic --suite-glob '*/*-sbml-l3v2.xml' --output-file results.md
```

- Use the `--help` option for more details or see the process script source code.