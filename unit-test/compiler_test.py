import unittest
import os
from gobjcreator3.compiler import CompileStep0 

_CURDIR = os.path.dirname(__file__)

class CompilerTest(unittest.TestCase):
    
    def setUp(self):
        
        pass
                    
    def tearDown(self):
        
        pass
        
    def testStep0(self):
        
        step = CompileStep0()
        root = step.process_file(_CURDIR + os.sep + "mydemo.goc3")
        
        print([(m.name, m.filepath_origin) for m in root.modules])
        
        demo = root.get_module("demo")
        print([(m.name, m.filepath_origin) for m in demo.modules])
        print([(t.get_fullname(), t.filepath_origin) for t in demo.types])
        print([(o.get_fullname(), o.filepath_origin) for o in demo.objects])
                                  
if __name__ == "__main__":
    
    unittest.main()

