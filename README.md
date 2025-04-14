# SBML Showcase
[![Continuous build using OMV](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/omv-ci.yml/badge.svg)](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/omv-ci.yml) [![Testing non OMV scripts](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/non-omv.yml/badge.svg)](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/non-omv.yml)

This repository is intended to highlight and show examples of interactions between the Systems Biology Markup Language (SBML) and Simulation Experiment Description Markup Language (SED-ML) and NeuroML/Open Source Brain. 

The repository contains files and instructions for testing validity of Systems Biology Markup Language (SBML) and Simulation Experiment Description Markup Language (SED-ML) files, and their compatibility with different simulations engines. Much of this functionality has been embedded in [pyNeuroML](https://docs.neuroml.org/Userdocs/Software/pyNeuroML.html).

## Testing validity of SBML/SEDML and compatability with simulation engines

The tables below show the results of some automated simulation pipelines for testing SBML/SEDML files.

### SBML
- [LEMS_NML2_Ex9_FN](SBML/tests/results_compatibility_biosimulators.md)

### BioModels
- [BioModels overview table](BioModels/README.md)
- [BIOMD0000000001](BioModels/BIOMD0000000001/tests/results_BIOMD0000000001_url.md)
- [BIOMD0000000138](BioModels/BIOMD0000000138/tests/results_BIOMD0000000138_url.md)
- [BIOMD0000000724](BioModels/BIOMD0000000724/tests/results_Theinmozhi_2018.md)
- [BIOMD0000001077](BioModels/BIOMD0000001077/tests/results_Adlung2021_model_jakstat_pa.md)

### Test Suite
- [Test Suite overview table](test_suite/results.md)
- [00001](test_suite/test_00001/tests/results_compatibility_biosimulators.md)
- [01186](test_suite/test_01186/tests/results_compatibility_biosimulators.md)

## Clone the Repository
To clone this repository to your local machine using the following command:

```sh
git clone https://github.com/OpenSourceBrain/SBMLShowcase.git
cd SBMLShowcase
```

## Conda environment
To set up a conda environment for the code in the SBML, BioModels, and test_suite folders.
```
conda create -n sbmlshowcase -c conda-forge python=3.10
conda activate sbmlshowcase
pip install -e .
conda activate sbmlshowcase
```
### for developers
```
conda create -n sbmlshowcase-dev -c conda-forge python=3.10
conda activate sbmlshowcase-dev
pip install -e .[dev]
conda activate sbmlshowcase-dev
```
To install the pre-commit hooks
```
pre-commit install
```
## Main Folders

The repository is organized into several folders each serving a specific purpose. Some of the key folders are:

- [**SBML**](SBML) Contains scripts and files related to a few simple SBML models and testing their compatibility with different BioSimulator engines.
- [**BioModels**](BioModels) Includes scripts for parsing and testing the compatibility of [BioModels](https://www.ebi.ac.uk/biomodels/) with various BioSimulator engines.
- [**test_suite**](test_suite) Holds test cases and scripts for validating the functionality of the repository's tools and models.
- [**utils**](utils) containing general functions.

## SBML
[**SBML**](SBML) contains a simple SBML model [`LEMS_NML2_Ex9_FN.sbml`](SBML/LEMS_NML2_Ex9_FN.sbml) and it's simulation file [`LEMS_NML2_Ex9_FN_missing_xmlns.sedml`](SBML/LEMS_NML2_Ex9_FN_missing_xmlns.sedml).

[test_compatibility_biosimulators](SBML/tests/test_compatibility_biosimulators.py) adds any missing XML or FBC namespaces to the SED-ML file, wraps up the SBML and SED-ML files into an Open Modeling EXchange format (OMEX) file, submits the OMEX file to different BioSimulator engines either locally via docker (indicated with an `L` for local in the results table), or remotely through the BioSimulators API (indicated with an `R`). The results table created by this script can be found in [here](SBML/tests/results_compatibility_biosimulators.md).

To run the script, change your directory to the SBML folder and run:

```
python test_compatibility_biosimulators.py
```

The following scripts test specific components of the process described above and are mainly run as workflows in GitHub Actions.
- [test_biosimulators_api](SBML/tests/test_biosimulators_api.py)
- [test_biosimulators_docker](SBML/tests/test_biosimulators_docker.py) 
- [test_biosimulators_local](SBML/tests/test_biosimulators_local.py) 
- [test_biosimulators_remote](SBML/tests/test_biosimulators_remote.py) 
- [test_compatibility_biosimulators](SBML/tests/test_compatibility_biosimulators.py) 
- [test_tellurium](SBML/tests/test_tellurium.py)

## BioModels
### Overview with all curated BioModels

[parse_biomodels](BioModels/parse_biomodels.py) creates an overview table in [`BioModels/README.md`](BioModels/README.md), testing curated [BioModels](https://www.ebi.ac.uk/biomodels/).

To run the script, change your directory to the BioModels folder and run:

```
python parse_biomodels.py
```
### Test specific BioModels
[test_biomodels_compatibility_biosimulators](BioModels/test_biomodels_compatibility_biosimulators.py)
tests engine compatibility of BioModels listed in `biomodel_id_list` ([BIOMD0000000001](https://www.ebi.ac.uk/biomodels/BIOMD0000000001), [BIOMD0000000138](https://www.ebi.ac.uk/biomodels/BIOMD0000000138), [BIOMD0000000724](https://www.ebi.ac.uk/biomodels/BIOMD0000000724), [BIOMD0000001077](https://www.ebi.ac.uk/biomodels/BIOMD0000001077)) and creates subfolders containing the results. Results can be found in `BioModels/BIOMOD_id/tests/results_BioModel_name.md`. 

For example for BioModel [BIOMD0000000001](https://www.ebi.ac.uk/biomodels/BIOMD0000000001), results can be found [here](BioModels/BIOMD0000000001/tests/results_BIOMD0000000001_url.md).

## test_suite
### Overview with semantic test suite cases
Processes the [semantic](https://github.com/sbmlteam/sbml-test-suite/tree/release/cases/semantic) [SBML Test Suite](https://github.com/sbmlteam/sbml-test-suite?tab=readme-ov-file) test cases which should all be valid SBML models with deterministic simulation results.

[process_test_suite](test_suite/process_test_suite.py) creates an overview table summarising whether the SBML files, SBML units, and SED-ML files are valid. In addition to that it shows whether the XML SBML namespaces (`xmlns-sbml`) are missing, and whether the models can be run (`pass` / `FAIL`) in tellurium natively, or remotely through the BioSimulators API. The table can be found [here](test_suite/results.md).

To run the script, change your directory to the test_suite folder and run:

```
python process_test_suite.py
```

There are several command line options for testing a limited amount of cases or specific test suite cases, see the [test_suite README](test_suite/README.md) for more information.


### Testing specific test suite cases
[test_test_suite_compatibility_biosimulators](test_suite/test_test_suite_compatibility_biosimulators.py) tests engine compatibility of specific semantic test suite cases (00001, 01186) Results can be found in `test_suite/test_case_id/tests/results_compatibility_biosimulators.md`. 

For example for for semantic test case [00001](https://www.ebi.ac.uk/biomodels/BIOMD0000000001), results can be found [here](test_suite/test_00001/tests/results_compatibility_biosimulators.md).

To run the script, change your directory to the test_suite folder and run:

```
python test_test_suite_compatibility_biosimulators.py
```
There are several command line options in the [test_suite README](test_suite/README.md).

# Converting NeuroML2/LEMS to & from SBML

Most of the interactions between [SBML](https://sbml.org) and LEMS/NeuroML showcased here are enabled by:

-   The SBML to LEMS import function in: [org.neuroml.importer](https://github.com/NeuroML/org.neuroml.import/blob/master/src/main/java/org/neuroml/importer/sbml/SBMLImporter.java)

-   The LEMS/NeuroML to SBML export function in: [org.neuroml.export](https://github.com/NeuroML/org.neuroml.export/blob/master/src/main/java/org/neuroml/export/sbml/SBMLWriter.java)

Note these features can be accessed easily with the [pyNeuroML](https://docs.neuroml.org/Userdocs/Software/pyNeuroML.html) tool. For example:

-   Load LEMSFile.xml using pyNeuroML, and convert it to SBML format:

         pynml LEMSFile.xml -sbml

-   Load LEMSFile.xml using pyNeuroML, and convert it to SBML format with a SED-ML specification for the experiment:

         pynml LEMSFile.xml -sbml-sedml

-   Load SBMLFile.sbml using jSBML, and convert it to LEMS format using values for duration & dt in ms

        pynml -sbml-import SBMLFile.sbml duration dt

See also https://github.com/ModECI/modelspec/blob/main/examples/COMBINE.md.



