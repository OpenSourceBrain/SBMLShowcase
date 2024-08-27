# Tabulating Validation Test Results on the SBML Test Suite

The `process_test_suite.py` script is designed to evaluate SBML files using the pyneuroml library. 

It currently runs three validation tests: 
1. Standard SBML validation.
2. SBML validation with strict unit checks.
3. SEDML validation, where SEDML files are assumed to have the same base filename as the SBML files but with a `-sedml.xml` extension instead of `.xml`.

The output is a markdown file containing a simple table of the results obtained on each file, where each test result is recorded as either a `pass` or `FAIL`.

## Getting Started

### Step 1: Download the Test Suite
Download the [zipfile](https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests_with_sedml_and_graphs.v3.4.0.zip) (or the latest equivalent) of the [SBML test suite](https://github.com/sbmlteam/sbml-test-suite) that includes [SEDML](https://github.com/SED-ML/sed-ml) files.

### Step 2: Extract the Files
Extract the downloaded ZIP file to a desired location, for example using the `unzip` command:

```bash
unzip semantic_tests_with_sedml_and_graphs.v3.4.0.zip -d /path_to_extraction_folder
```

### Step 3: Set up the right environment
```
pip install matplotlib
pip install pyneuroml
pip install pyneuroml[combine]
pip install pyneuroml[tellurium]
pip install pymetadata
pip install docker
```

### Step 3: Run the Validation Script
Navigate to the directory containing the `process_test_suite.py` script and execute it, specifying the path to the extracted test files. For example if the extraction folder is  `C:\Users\Username\Documents\compbiolibs\SBML_test_suite\semantic` and the `process_test_suite.py` script is in the current directory.

```
 python process_test_suite.py --suite-path C:\Users\Username\Documents\compbiolibs\SBML_test_suite\semantic  --sbml-level_version 'sbml-l3v2' --output-file ./results_test.md --limit 5       
```

## Command Line Options

The `process_test_suite.py` script provides various command-line options to customize the execution of the tests. Below are the available options.

- `--limit`  
  **Description:** Limits the number of test cases processed.  
  **Usage:** `--limit <number>`  
  **Default:** `0` (no limit)

- `--suite-path`  
  **Description:** Specifies the path to the directory containing the test suite files.  
  **Usage:** `--suite-path <path>`  
  **Default:** `.` (current directory)

- `--sbml-level_version'
  **Description:** String that specifies level and version of files to select for processing (e.g. 'l3v2')
  **Usage:** `--sbml-level_version <string>`  
  **Default:** `highest`

- `--suite-url-base`  
  **Description:** Base URL for the online test case files to include as links in the results. Set to an empty string to disable links.  
  **Usage:** `--suite-url-base <url>`  
  **Default:** `https://github.com/sbmlteam/sbml-test-suite/blob/release/cases/semantic`

- `--output-file`  
  **Description:** Specifies the path to the output file where the results will be written.  
  **Usage:** `--output-file <file path>`  
  **Default:** `results.md`

Each option can be used to modify the behavior of the script to fit specific needs, such as limiting the number of cases to process for testing purposes or specifying a different output file for the results.
