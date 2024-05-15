#!/usr/bin/env python

'''
use pymetadata module to create a minimal valid combine archive
using LEMS_NML2_Ex9_FN.sbml and LEMS_NML2_Ex9_FN.sedml
'''

import sys
sys.path.append("..")
import utils

sbml_file = 'LEMS_NML2_Ex9_FN.sbml'
sedml_file = 'LEMS_NML2_Ex9_FN.sedml'


#utils.create_omex(sedml_file,sbml_file)

message = utils.run_biosimulators_docker('tellurium',sedml_file,sbml_file)[1][3:-3]

print(message)
