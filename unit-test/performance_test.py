import os
import cProfile
from gobjcreator3.compiler import Compiler
from gobjcreator3.codegen.c_code_generator import CCodeGenerator, CGenConfig
from gobjcreator3.codegen.output import NullOut

_CURDIR = os.path.dirname(__file__)

goc3_filepath = _CURDIR + os.sep + "test.goc3"
model = Compiler().compile(goc3_filepath)

def generate_code():

    CCodeGenerator(model, 
                   goc3_filepath, 
                   out=NullOut(),
                   config=CGenConfig()).generate()

cProfile.run("generate_code()", sort='calls')
