import unittest
import os
from gobjcreator3.gobjcreator_parser import GobjcreatorParser

_CURDIR = os.path.dirname(__file__)

class ParserTest(unittest.TestCase):
    
    def setUp(self):
        
        self.parser = GobjcreatorParser()
            
    def tearDown(self):
        
        self.parser = None
        
    def testMyDemo(self):
        
        try:
            ast = self.parser.parseFile(_CURDIR + os.sep + "mydemo.goc3")
            self.assertIsNotNone(ast)
            print(ast.toXml())
        except Exception as error:
            self.fail("ParseError: %s" % error)
        
if __name__ == "__main__":
    
    unittest.main()

