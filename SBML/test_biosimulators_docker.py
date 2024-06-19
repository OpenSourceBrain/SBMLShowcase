#!/usr/bin/env python

'''
use pymetadata module to create a minimal valid combine archive
using LEMS_NML2_Ex9_FN.sbml and LEMS_NML2_Ex9_FN.sedml
'''

import sys
sys.path.append("..")
import utils

sbml_filepath = 'LEMS_NML2_Ex9_FN.sbml'
#sedml_filepath = 'LEMS_NML2_Ex9_FN.sedml' #xmlns:sbml added manually
sedml_filepath = 'LEMS_NML2_Ex9_FN_missing_xmlns.sedml' #xmlns:sbml missing
omex_filepath = utils.create_omex(sedml_filepath,sbml_filepath)

utils.biosimulators_core('tellurium',omex_filepath)

print('Finished')
