import unittest
import os
from gobjcreator3.compiler import Compiler
from gobjcreator3.model.type import Type 

_CURDIR = os.path.dirname(__file__)

class CompilerTest(unittest.TestCase):
    
    def setUp(self):
        
        pass
                    
    def tearDown(self):
        
        pass
        
    def testStep0(self):
        
        root = Compiler().compile(_CURDIR + os.sep + "mydemo.goc3")
        
        print([(m.get_fullname(), m.filepath_origin) for m in root.modules])
                
        demo = root.get_module("demo")
        print([(m.get_fullname(), m.filepath_origin) for m in demo.modules])
        print([(t.get_fullname(), t.filepath_origin) for t in demo.types])
        print([(o.get_fullname(), o.filepath_origin) for o in demo.objects])
        print([(e.get_fullname(), e.filepath_origin) for e in demo.error_domains])
        print([(f.get_fullname(), f.filepath_origin) for f in demo.flags])
        
        human = root.get_module("bio::human")
        print([(i.get_fullname(), i.filepath_origin) for i in human.interfaces])
        
        thread = demo.get_type_element("::os::threading::Thread")
        print(thread)
        print(thread.category == Type.OBJECT)
                                  
if __name__ == "__main__":
    
    unittest.main()

