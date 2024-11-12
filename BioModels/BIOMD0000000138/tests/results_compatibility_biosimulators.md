| Engine                                                                                                                                     | Compatibility                                                                                                                                                                                                                                            | pass / FAIL (R)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | pass / FAIL (L)                                                                                                                                                                                                                                                                                                                                                                                   | d1 (R)                                                                  | d1 (L)                                                                 |
|:-------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------|:-----------------------------------------------------------------------|
| <details><summary>AMICI</summary>https://docs.biosimulators.org/Biosimulators_AMICI/<br></details>                                         | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with amici.<br><br>['SBML', 'SED-ML'] are compatible with amici.</details>                                                 | <details><summary>&#10060; FAIL</summary><a href="https://api.biosimulations.org/runs/67323c8c0d09353e8f106b51">view</a><br><a href="https://api.biosimulations.org/results/67323c8c0d09353e8f106b51/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c8c0d09353e8f106b51?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>lambda * (phik - n) / taun<br><br>ERROR TYPE:<br>CombineArchiveExecutionError</details>                                                                                                                                                                                                                                 | <details><summary>&#10060; FAIL</summary>ERROR MESSAGE:<br>lambda * (phik - n) / taun<br><br>ERROR TYPE:<br>CombineArchiveExecutionError</details>                                                                                                                                                                                                                                                | <a href="d1_plots_remote\amici_autogen_plot_for_task1.pdf">plot</a>     | <a href="d1_plots_local\amici_autogen_plot_for_task1.pdf">plot</a>     |
| <details><summary>BioNetGen</summary>https://docs.biosimulators.org/Biosimulators_BioNetGen/<br></details>                                 | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with bionetgen.<br><br>['BNGL', 'SED-ML'] are compatible with bionetgen.</details>                      | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323c900d09353e8f106b54">view</a><br><a href="https://api.biosimulations.org/results/67323c900d09353e8f106b54/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c900d09353e8f106b54?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>`/root/archive.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details> | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details> |                                                                         |                                                                        |
| <details><summary>BoolNet</summary>https://docs.biosimulators.org/Biosimulators_BoolNet/<br></details>                                     | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with boolnet.<br><br>['SBML-qual', 'SED-ML'] are compatible with boolnet.</details>                     | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323c92b678b3883bb6c1d6">view</a><br><a href="https://api.biosimulations.org/results/67323c92b678b3883bb6c1d6/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c92b678b3883bb6c1d6?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>`/root/archive.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details> | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details> |                                                                         |                                                                        |
| <details><summary>Brian 2</summary>https://docs.biosimulators.org/Biosimulators_pyNeuroML/<br></details>                                   | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with brian2.<br><br>['NeuroML', 'SED-ML', 'LEMS', 'SED-ML'] are compatible with brian2.</details>       | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323c8eb678b3883bb6c1d2">view</a><br><a href="https://api.biosimulations.org/results/67323c8eb678b3883bb6c1d2/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c8eb678b3883bb6c1d2?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                      | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                                     |                                                                         |                                                                        |
| <details><summary>CBMPy</summary>https://docs.biosimulators.org/Biosimulators_CBMPy/<br></details>                                         | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with cbmpy.<br><br>['SBML', 'SED-ML'] are compatible with cbmpy.</details>                                                 | <details><summary>&#10060; FAIL</summary><a href="https://api.biosimulations.org/runs/67323c930d09353e8f106b57">view</a><br><a href="https://api.biosimulations.org/results/67323c930d09353e8f106b57/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c930d09353e8f106b57?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>`/root/archive.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      | <details><summary>&#10060; FAIL</summary>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      |                                                                         |                                                                        |
| <details><summary>COBRApy</summary>https://docs.biosimulators.org/Biosimulators_COBRApy/<br>Only allows steady state simulations</details> | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with cobrapy.<br><br>['SBML', 'SED-ML'] are compatible with cobrapy.</details>                                             | <details><summary>&#10060; FAIL</summary><a href="https://api.biosimulations.org/runs/67323c95b678b3883bb6c1dc">view</a><br><a href="https://api.biosimulations.org/results/67323c95b678b3883bb6c1dc/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c95b678b3883bb6c1dc?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>`/root/archive.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      | <details><summary>&#10060; FAIL</summary>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      |                                                                         |                                                                        |
| <details><summary>COPASI</summary>https://docs.biosimulators.org/Biosimulators_COPASI/<br></details>                                       | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with copasi.<br><br>['SBML', 'SED-ML'] are compatible with copasi.</details>                                               | <details><summary>&#9989; PASS</summary><a href="https://api.biosimulations.org/runs/67323c980d09353e8f106b5b">view</a><br><a href="https://api.biosimulations.org/results/67323c980d09353e8f106b5b/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c980d09353e8f106b5b?includeOutput=true">logs</a><br><br></details>                                                                                                                                                                                                                                                                                                                                 | &#9989; PASS                                                                                                                                                                                                                                                                                                                                                                                      | <a href="d1_plots_remote\copasi_autogen_plot_for_task1.pdf">plot</a>    | <a href="d1_plots_local\copasi_autogen_plot_for_task1.pdf">plot</a>    |
| <details><summary>GillesPy2</summary>https://docs.biosimulators.org/Biosimulators_GillesPy2/<br></details>                                 | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with gillespy2.<br><br>['SBML', 'SED-ML'] are compatible with gillespy2.</details>                                         | <details><summary>&#10060; FAIL</summary><a href="https://api.biosimulations.org/runs/67323c9a5a60072d20f56d8d">view</a><br><a href="https://api.biosimulations.org/results/67323c9a5a60072d20f56d8d/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c9a5a60072d20f56d8d?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>`/root/archive.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      | <details><summary>&#10060; FAIL</summary>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      |                                                                         |                                                                        |
| <details><summary>GINsim</summary>https://docs.biosimulators.org/Biosimulators_GINsim/<br></details>                                       | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with ginsim.<br><br>['SBML-qual', 'SED-ML'] are compatible with ginsim.</details>                       | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323c9c5a60072d20f56d90">view</a><br><a href="https://api.biosimulations.org/results/67323c9c5a60072d20f56d90/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c9c5a60072d20f56d90?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>`/root/archive.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details> | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details> |                                                                         |                                                                        |
| <details><summary>LibSBMLSim</summary>https://docs.biosimulators.org/Biosimulators_LibSBMLSim/<br></details>                               | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with libsbmlsim.<br><br>['SBML', 'SED-ML'] are compatible with libsbmlsim.</details>                                       | <details><summary>&#10060; FAIL</summary><a href="https://api.biosimulations.org/runs/67323c9eb678b3883bb6c1ec">view</a><br><a href="https://api.biosimulations.org/results/67323c9eb678b3883bb6c1ec/download">download</a><br><a href="https://api.biosimulations.org/logs/67323c9eb678b3883bb6c1ec?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>`/root/archive.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      | <details><summary>&#10060; FAIL</summary>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      |                                                                         |                                                                        |
| <details><summary>MASSpy</summary>https://docs.biosimulators.org/Biosimulators_MASSpy/<br></details>                                       | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with masspy.<br><br>['SBML', 'SED-ML'] are compatible with masspy.</details>                                               | <details><summary>&#10060; FAIL</summary><a href="https://api.biosimulations.org/runs/67323ca05a60072d20f56da2">view</a><br><a href="https://api.biosimulations.org/results/67323ca05a60072d20f56da2/download">download</a><br><a href="https://api.biosimulations.org/logs/67323ca05a60072d20f56da2?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>The COMBINE/OMEX did not execute successfully:<br><br>  The SED document did not execute successfully:<br>  <br>    Something went wrong reading the SBML model. Most likely the SBML model is not valid. Please check that your model is valid using the `mass.io.sbml.validate_sbml_model` function or via the online validator at http://sbml.org/validator .<br>    	`(model, errors) = validate_sbml_model(filename)`<br>    If the model is valid and cannot be read please open an issue at https://github.com/SBRG/masspy/issues .<br><br>ERROR TYPE:<br>CombineArchiveExecutionError</details>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | <details><summary>&#10060; FAIL</summary>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details>                      | <a href="d1_plots_remote\masspy_autogen_plot_for_task1.pdf">plot</a>    |                                                                        |
| <details><summary>NetPyNE</summary>https://docs.biosimulators.org/Biosimulators_pyNeuroML/<br></details>                                   | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with netpyne.<br><br>['NeuroML', 'SED-ML', 'LEMS', 'SED-ML'] are compatible with netpyne.</details>     | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323ca1b678b3883bb6c200">view</a><br><a href="https://api.biosimulations.org/results/67323ca1b678b3883bb6c200/download">download</a><br><a href="https://api.biosimulations.org/logs/67323ca1b678b3883bb6c200?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                      | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                                     |                                                                         |                                                                        |
| <details><summary>NEURON</summary>https://docs.biosimulators.org/Biosimulators_pyNeuroML/<br></details>                                    | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with neuron.<br><br>['NeuroML', 'SED-ML', 'LEMS', 'SED-ML'] are compatible with neuron.</details>       | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323ca30d09353e8f106b76">view</a><br><a href="https://api.biosimulations.org/results/67323ca30d09353e8f106b76/download">download</a><br><a href="https://api.biosimulations.org/logs/67323ca30d09353e8f106b76?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                      | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                                     |                                                                         |                                                                        |
| <details><summary>OpenCOR</summary>https://docs.biosimulators.org/Biosimulators_OpenCOR/<br></details>                                     | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with opencor.<br><br>['CellML', 'SED-ML'] are compatible with opencor.</details>                        | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323ca40d09353e8f106b7d">view</a><br><a href="https://api.biosimulations.org/results/67323ca40d09353e8f106b7d/download">download</a><br><a href="https://api.biosimulations.org/logs/67323ca40d09353e8f106b7d?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                      | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                                     |                                                                         |                                                                        |
| <details><summary>pyNeuroML</summary>https://docs.biosimulators.org/Biosimulators_pyNeuroML/<br></details>                                 | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with pyneuroml.<br><br>['NeuroML', 'SED-ML', 'LEMS', 'SED-ML'] are compatible with pyneuroml.</details> | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323ca60d09353e8f106b82">view</a><br><a href="https://api.biosimulations.org/results/67323ca60d09353e8f106b82/download">download</a><br><a href="https://api.biosimulations.org/logs/67323ca60d09353e8f106b82?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                      | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                                     |                                                                         |                                                                        |
| <details><summary>PySCeS</summary>https://docs.biosimulators.org/Biosimulators_PySCeS/<br></details>                                       | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with pysces.<br><br>['SBML', 'SED-ML'] are compatible with pysces.</details>                                               | <details><summary>&#10060; FAIL</summary><a href="https://api.biosimulations.org/runs/67323ca80d09353e8f106b87">view</a><br><a href="https://api.biosimulations.org/results/67323ca80d09353e8f106b87/download">download</a><br><a href="https://api.biosimulations.org/logs/67323ca80d09353e8f106b87?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>The COMBINE/OMEX did not execute successfully:<br><br>  The SED document did not execute successfully:<br>  <br>    class 'AttributeError':'PysMod' object has no attribute 'lambda'<br><br>ERROR TYPE:<br>CombineArchiveExecutionError</details>                                                                       | <details><summary>&#10060; FAIL</summary>ERROR MESSAGE:<br>The COMBINE/OMEX did not execute successfully:<br><br>  The SED document did not execute successfully:<br>  <br>    class 'AttributeError':'PysMod' object has no attribute 'lambda'<br><br>ERROR TYPE:<br>CombineArchiveExecutionError</details>                                                                                      | <a href="d1_plots_remote\pysces_autogen_plot_for_task1.pdf">plot</a>    | <a href="d1_plots_local\pysces_autogen_plot_for_task1.pdf">plot</a>    |
| <details><summary>RBApy</summary>https://docs.biosimulators.org/Biosimulators_RBApy/<br></details>                                         | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with rbapy.<br><br>['RBApy', 'SED-ML'] are compatible with rbapy.</details>                             | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323ca9b678b3883bb6c229">view</a><br><a href="https://api.biosimulations.org/results/67323ca9b678b3883bb6c229/download">download</a><br><a href="https://api.biosimulations.org/logs/67323ca9b678b3883bb6c229?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>`/root/archive.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details> | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>`/root/in/BIOMD0000000138_url.omex` is not a valid COMBINE/OMEX archive.<br>  - The SED-ML file at location `./BIOMD0000000138_url.sedml` is invalid.<br>    - Simulation `auto_ten_seconds` is invalid.<br>      - Algorithm has an invalid KiSAO id `KISAO_0000694`.<br><br>ERROR TYPE:<br>ValueError</details> |                                                                         |                                                                        |
| <details><summary>Smoldyn</summary>https://smoldyn.readthedocs.io/en/latest/python/api.html#sed-ml-combine-biosimulators-api<br></details> | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with smoldyn.<br><br>['Smoldyn', 'SED-ML'] are compatible with smoldyn.</details>                       | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323cab0d09353e8f106b90">view</a><br><a href="https://api.biosimulations.org/results/67323cab0d09353e8f106b90/download">download</a><br><a href="https://api.biosimulations.org/logs/67323cab0d09353e8f106b90?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                      | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>Error unknown. The log.yml containing error information was not found.<br><br></details>                                                                                                                                                                                                                          |                                                                         |                                                                        |
| <details><summary>Tellurium</summary>https://docs.biosimulators.org/Biosimulators_tellurium/<br></details>                                 | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with tellurium.<br><br>['SBML', 'SED-ML'] are compatible with tellurium.</details>                                         | <details><summary>&#9989; PASS</summary><a href="https://api.biosimulations.org/runs/67323cad5a60072d20f56dd1">view</a><br><a href="https://api.biosimulations.org/results/67323cad5a60072d20f56dd1/download">download</a><br><a href="https://api.biosimulations.org/logs/67323cad5a60072d20f56dd1?includeOutput=true">logs</a><br><br></details>                                                                                                                                                                                                                                                                                                                                 | &#9989; PASS                                                                                                                                                                                                                                                                                                                                                                                      | <a href="d1_plots_remote\tellurium_autogen_plot_for_task1.pdf">plot</a> | <a href="d1_plots_local\tellurium_autogen_plot_for_task1.pdf">plot</a> |
| <details><summary>VCell</summary>https://github.com/virtualcell/vcell<br></details>                                                        | <details><summary>&#10067; UNSURE</summary>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with vcell.<br><br>['SBML', 'SED-ML', 'BNGL', 'SED-ML'] are compatible with vcell.</details>                               | <details><summary>&#10060; FAIL</summary><a href="https://api.biosimulations.org/runs/67323caf5a60072d20f56dd9">view</a><br><a href="https://api.biosimulations.org/results/67323caf5a60072d20f56dd9/download">download</a><br><a href="https://api.biosimulations.org/logs/67323caf5a60072d20f56dd9?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>status: QUEUED<br><br></details>                                                                                                                                                                                                                                                                                        | &#9989; PASS                                                                                                                                                                                                                                                                                                                                                                                      |                                                                         | <a href="d1_plots_local\vcell_autogen_plot_for_task1.pdf">plot</a>     |
| <details><summary>XPP</summary>https://docs.biosimulators.org/Biosimulators_XPP/<br></details>                                             | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>The file extensions ('xml', 'sedml') suggest the input file types may be compatibe with xpp.<br><br>['XPP', 'SED-ML'] are compatible with xpp.</details>                                   | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br><a href="https://api.biosimulations.org/runs/67323cb15a60072d20f56ddf">view</a><br><a href="https://api.biosimulations.org/results/67323cb15a60072d20f56ddf/download">download</a><br><a href="https://api.biosimulations.org/logs/67323cb15a60072d20f56ddf?includeOutput=true">logs</a><br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                      | <details><summary>&#9888; XFAIL</summary>EXPECTED FAIL<br><br>ERROR MESSAGE:<br>No module named 'libsbml'<br><br>ERROR TYPE:<br>ModuleNotFoundError</details>                                                                                                                                                                                                                                     |                                                                         |                                                                        |