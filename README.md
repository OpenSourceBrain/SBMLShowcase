### Converting NeuroML2/LEMS to & from SBML

Most of the interactions between SBML and LEMS/NeuroML showcased here are enabled by:

-   The SBML to LEMS import function in: [org.neuroml.importer](https://github.com/NeuroML/org.neuroml.import/blob/master/src/main/java/org/neuroml/importer/sbml/SBMLImporter.java)

-   The LEMS/NeuroML to SBML export function in: [org.neuroml.export](https://github.com/NeuroML/org.neuroml.export/blob/master/src/main/java/org/neuroml/export/sbml/SBMLWriter.java)

Note these features can be accessed easily with the [jNeuroML](https://github.com/NeuroML/jNeuroML) tool. For example:

-   Load LEMSFile.xml using jLEMS, and convert it to SBML format:

         jnml LEMSFile.xml -sbml

-   Load LEMSFile.xml using jLEMS, and convert it to SBML format with a SED-ML specification for the experiment:

         jnml LEMSFile.xml -sbml-sedml

-   Load SBMLFile.sbml using jSBML, and convert it to LEMS format using values for duration & dt in ms

        jnml -sbml-import SBMLFile.sbml duration dt


[![Build Status](https://travis-ci.org/OpenSourceBrain/SBMLShowcase.svg?branch=master)](https://travis-ci.org/OpenSourceBrain/SBMLShowcase)

