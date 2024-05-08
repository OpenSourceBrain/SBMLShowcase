#!/usr/bin/python

'''
use pymetadata module to create a minimal valid combine archive
using LEMS_NML2_Ex9_FN.sbml and LEMS_NML2_Ex9_FN.sedml
'''

sys.path.append("..")
import utils

sbml_file = 'LEMS_NML2_Ex9_FN.sbml'
sedml_file = 'LEMS_NML2_Ex9_FN.sedml'

utils.create_omex(sedml_file,sbml_file)
