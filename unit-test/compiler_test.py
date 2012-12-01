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
        
    def testCompileSteps(self):
        
        root = Compiler().compile(_CURDIR + os.sep + "mydemo.goc3")
        
        print([(m.get_fullname(), m.filepath_origin) for m in root.modules])
                
        demo = root.get_module("demo")
        print([(m.get_fullname(), m.filepath_origin) for m in demo.modules])
        print([(t.get_fullname(), t.filepath_origin) for t in demo.types])
        print([(o.get_fullname(), o.filepath_origin) for o in demo.objects])
        print([(e.get_fullname(), e.filepath_origin) for e in demo.error_domains])
        print([(f.get_fullname(), f.filepath_origin) for f in demo.flags])
        
        human = root.get_module("bio/human")
        print([(i.get_fullname(), i.filepath_origin) for i in human.interfaces])

        worker = demo.get_object("Worker")
        print([(i.get_fullname(), i.filepath_origin) for i in worker.interfaces])
        method = worker.get_method("create")
        for p in method.parameters:
            print("%s: %s" % (p.name, p.type))
        
        thread = demo.get_type_element("../os/threading/Thread")
        print(thread)
        print(thread.category == Type.OBJECT)
        
        employee = root.get_interface("company/Employee")
        print([m.name for m in employee.methods])
        
                                  
if __name__ == "__main__":
    
    unittest.main()

