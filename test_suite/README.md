# Tabulating Validation Test Results on the SBML Test Suite

The `process_test_suite.py` script is designed to evaluate SBML files using the pyneuroml library. 

It currently runs three validation tests: 
1. Standard SBML validation.
2. SBML validation with strict unit checks.
3. SEDML validation, where SEDML files are assumed to have the same base filename as the SBML files but with a `-sedml.xml` extension instead of `.xml`.

The output is a markdown file containing a simple table of the results obtained on each file, where each test result is recorded as either a `pass` or `FAIL`.

## Run the Validation Script

Navigate to the test_suite directory and run for example

```
 python process_test_suite.py --cases 00001 00002 00011 --sbml-level_version l1v2 --output-file results_00001_00002_00011.md
```
or to run all test cases using the highest SBML versions available navigate to the test_suite directory and run (overwrites `results.md`)

```
 python process_test_suite.py 
```
## Test specific cases
Navigate to the test_suite directory and run for example

```
test_test_suite_compatibility_biosimulators.py --cases 00006 01280 --sbml-level_version highest
```
or to run test cases 00001 and 01186 (tested in this repository) using the highest SBML versions available navigate to the test_suite directory and run

```
test_test_suite_compatibility_biosimulators.py 
```

## Command Line Options

- `--limit`  
  **Description:** Limits the number of test cases processed.  
  **Usage:** `--limit <number>`  
  **Default:** `0` (no limit)

- `--cases`  
  **Description:** List specific cases to process.  
  **Usage:** `--cases <list>`  
  **Default:** `[]` (no limit)

- `--suite-path`  
  **Description:** Specifies the path to the directory containing the test suite files.  
  **Usage:** `--suite-path <path>`  
  **Default:** `.` (current directory)

- `--sbml-level_version`  
  **Description:** String that specifies the level and version of files to select for processing (e.g., 'l3v2').  
  **Usage:** `--sbml-level_version <string>`  
  **Default:** `highest`

- `--suite-url-base`  
  **Description:** Base URL for the online test case files to include as links in the results. Set to an empty string to disable links.  
  **Usage:** `--suite-url-base <url>`  
  **Default:** `https://github.com/sbmlteam/sbml-test-suite/blob/release/cases/semantic`

 ### process_test_suite only
- `--skip`  
  **Description:** Skip cases listed.  
  **Usage:** `--skip <list>`  
  **Default:** `[]` (no skip)

- `--output-file`  
  **Description:** Specifies the path to the output file where the results will be written.  
  **Usage:** `--output-file <file path>`  
  **Default:** `results.md`

