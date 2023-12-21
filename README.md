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
