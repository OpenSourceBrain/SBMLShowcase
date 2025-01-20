# SBML Showcase
This repository contains files and instructions for testing validity of Systems Biology Markup Language (SBML) and Simulation Experiment Description Markup Language (SED-ML) files, and their compatibility with different simulations engines. 

## Clone the Repository
To clone this repository to your local machine using the following command:

```sh
git clone https://github.com/OpenSourceBrain/SBMLShowcase.git
cd SBMLShowcase
```

## Install requirements
To set up a conda environment for the code in the SBML, BioModels, and test_suite folders.
```
conda create -n sbmlshowcase -c conda-forge python=3.10
conda activate sbmlshowcase
pip install -e .
conda activate sbmlshowcase
```
or for developers
```
conda create -n sbmlshowcase-dev -c conda-forge python=3.10
conda activate sbmlshowcase-dev
pip install -e .[dev]
conda activate sbmlshowcase-dev
```
## Folders
### BioModels
Top level of this folder contains two scripts.

#### parse_biomodels.py
Creates an overview table in `BioModels/README.md`, testing all available [BioModels](https://www.ebi.ac.uk/biomodels/).

To run the script, navigate to the BioModels directory and run:

```
python parse_biomodels.py
```

#### test_biomodels_compatibility_biosimulators.py
Tests engine compatibility of specific [BioModels](https://www.ebi.ac.uk/biomodels/) and creates subfolders containing the results. Results can be found in `BioModels/BIOMOD_id/tests/results_BioModel_name.md`.

For example for BioModel [BIOMD0000000001](https://www.ebi.ac.uk/biomodels/BIOMD0000000001)
`BioModels/BIOMD0000000001/tests/results_BIOMD0000000001_url.md` 

### SBML


### test_suite


# Converting NeuroML2/LEMS to & from SBML

[![Continuous build using OMV](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/omv-ci.yml/badge.svg)](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/omv-ci.yml) [![Testing non OMV scripts](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/non-omv.yml/badge.svg)](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/non-omv.yml)

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

