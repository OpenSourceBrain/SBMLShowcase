# SBML Showcase

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Tests status][tests-badge]][tests-link]
[![Linting status][linting-badge]][linting-link]
[![Documentation status][documentation-badge]][documentation-link]
[![License][license-badge]](./LICENSE.md)

## Converting NeuroML2/LEMS to & from SBML

[![Continuous build using OMV](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/omv-ci.yml/badge.svg)](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/omv-ci.yml) [![Testing non OMV scripts](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/non-omv.yml/badge.svg)](https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/non-omv.yml)

Most of the interactions between [SBML](https://sbml.org) and LEMS/NeuroML showcased here are enabled by:

- The SBML to LEMS import function in: [org.neuroml.importer](https://github.com/NeuroML/org.neuroml.import/blob/master/src/main/java/org/neuroml/importer/sbml/SBMLImporter.java)

- The LEMS/NeuroML to SBML export function in: [org.neuroml.export](https://github.com/NeuroML/org.neuroml.export/blob/master/src/main/java/org/neuroml/export/sbml/SBMLWriter.java)

Note these features can be accessed easily with the [pyNeuroML](https://docs.neuroml.org/Userdocs/Software/pyNeuroML.html) tool. For example:

- Load LEMSFile.xml using pyNeuroML, and convert it to SBML format:

         pynml LEMSFile.xml -sbml

- Load LEMSFile.xml using pyNeuroML, and convert it to SBML format with a SED-ML specification for the experiment:

         pynml LEMSFile.xml -sbml-sedml

- Load SBMLFile.sbml using jSBML, and convert it to LEMS format using values for duration & dt in ms

        pynml -sbml-import SBMLFile.sbml duration dt

See also <https://github.com/ModECI/modelspec/blob/main/examples/COMBINE.md>.

## setup instructions

### Step 1: Clone the Repository

```
clone https://github.com/yourusername/SBMLShowcase.git
cd SBMLShowcase
```

### Step 2: Create an Environment (e.g. conda)

```
conda create -n sbmlshowcase-dev -c conda-forge python=3.10
conda activate sbmlshowcase-dev
pip install -e .
```

<!-- prettier-ignore-start -->
[tests-badge]:              https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/tests.yml/badge.svg
[tests-link]:               https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/tests.yml
[linting-badge]:            https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/linting.yml/badge.svg
[linting-link]:             https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/linting.yml
[documentation-badge]:      https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/docs.yml/badge.svg
[documentation-link]:       https://github.com/OpenSourceBrain/SBMLShowcase/actions/workflows/docs.yml
[license-badge]:            https://img.shields.io/badge/License-BSD_3--Clause-blue.svg
<!-- prettier-ignore-end -->

Tests SBML compatibility with BioSimulators registered simulation engines

This project is developed in collaboration with the
[Centre for Advanced Research Computing](https://ucl.ac.uk/arc), University
College London.

## About

### Project Team

Open Source Brain ([info@opensourcebrain.org](mailto:info@opensourcebrain.org))

<!-- TODO: how do we have an array of collaborators ? -->

### Research Software Engineering Contact

Centre for Advanced Research Computing, University College London
([arc.collaborations@ucl.ac.uk](mailto:arc.collaborations@ucl.ac.uk))

## Getting Started

### Prerequisites

<!-- Any tools or versions of languages needed to run code. For example specific Python or Node versions. Minimum hardware requirements also go here. -->

`SBMLShowcase` requires Python 3.9 or higher

### Installation

<!-- How to build or install the application. -->

We recommend installing in a project specific virtual environment created using
a environment management tool such as
[Conda](https://docs.conda.io/projects/conda/en/stable/). To install the latest
development version of `SBMLShowcase` using `pip` in the currently active
environment run

```sh
pip install git+https://github.com/OpenSourceBrain/SBMLShowcase.git
```

Alternatively create a local clone of the repository with

```sh
git clone https://github.com/OpenSourceBrain/SBMLShowcase.git
```

and then install in editable mode by running in your (e.g. conda) environment

```sh
conda create -n sbmlshowcase-dev -c conda-forge python=3.10
conda activate sbmlshowcase-dev
pip install -e .
```

### Running Locally

How to run the application on your local system.

### Running Tests

<!-- How to run tests on your local system. -->

Tests can be run across all compatible Python versions in isolated environments
using [`tox`](https://tox.wiki/en/latest/) by running

```sh
tox
```

To run tests manually in a Python environment with `pytest` installed run

```sh
pytest tests
```

again from the root of the repository.

### Building Documentation

The MkDocs HTML documentation can be built locally by running

```sh
tox -e docs
```

from the root of the repository. The built documentation will be written to
`site`.

Alternatively to build and preview the documentation locally, in a Python
environment with the optional `docs` dependencies installed, run

```sh
mkdocs serve
```

## Acknowledgements

This work was funded by The Kavli Foundation.
