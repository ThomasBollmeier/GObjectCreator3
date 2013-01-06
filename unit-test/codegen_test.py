import unittest
import os
from gobjcreator3.compiler import Compiler
from gobjcreator3.codegen.c_code_generator import CCodeGenerator, CGenConfig


_CURDIR = os.path.dirname(__file__)

class CodeGeneratorTest(unittest.TestCase):
    
    def setUp(self):
        
        pass
                    
    def tearDown(self):
        
        pass
        
    def testCCodeGeneration(self):
        
        origin = _CURDIR + os.sep + "test.goc3"
        
        root = Compiler().compile(origin)
        
        config = CGenConfig()
        config.generate_setter_getter = True
                
        CCodeGenerator(root, origin, config=config).generate()
                                          
if __name__ == "__main__":
    
    unittest.main()

