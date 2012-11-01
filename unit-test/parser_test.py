import unittest
import os
from gobjcreator3.parser import GobjcreatorParser
from gobjcreator3.interpreter import Interpreter
from gobjcreator3.ast_visitor import AstVisitor
from gobjcreator3.parameter import Parameter

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
            
            interpreter = Interpreter()
            interpreter.eval_grammar(ast, TestVisitor())
                        
        except Exception as error:
            self.fail("ParseError: %s" % error)
            
class TestVisitor(AstVisitor):
    
    def __init__(self):
        
        AstVisitor.__init__(self)
        
        self._module_path = []
        self._indent_level = 0
        
    def visit_include_path(self, include_path):
        
        self._write("IncludePath: %s" % include_path)
                
    def enter_module(self, module_name):
        
        self._write("Module: %s" % self._absname(module_name))
        
        self._module_path.append(module_name)
        self._indent()
        
    def exit_module(self):
        
        self._module_path.pop()
        self._dedent()

    def visit_type_declaration(self, typename):
        
        self._write("GType: %s" % self._absname(typename))
                
    def enter_gobject(self, name):
        
        self._write("GObject: %s" % self._absname(name))
        self._indent()

    def exit_gobject(self):
        
        self._dedent()

    def enter_ginterface(self, name):
        
        self._write("GInterface: %s" % self._absname(name))
        self._indent()

    def exit_ginterface(self):
        
        self._dedent()

    def visit_gerror(self, name, codes):
        
        self._write("GError: %s" % self._absname(name))
        self._indent()
        for code in codes:
            self._write(code)
        self._dedent()

    def visit_genum(self, name, codeNamesValues):
        
        self._write("GEnum: %s" % self._absname(name))
        self._indent()
        for cname, cval in codeNamesValues:
            if cval is None:
                self._write(cname)
            else:
                self._write(cname + " = %s" % cval)
        self._dedent()

    def visit_gflags(self, name, codes):
        
        self._write("GFlags: %s" % self._absname(name))
        self._indent()
        for code in codes:
            self._write(code)
        self._dedent()

    def enter_method(self, name, attrs, parameters):

        self._write("Method: %s" % name)
        self._indent()
        self._write("Attributes: %s" % attrs)
        if parameters:
            self._write("Parameters:")
            self._indent()    
            for param in parameters:
                if param.category == Parameter.IN:
                    self._write("%s: %s (IN)" % (param.name, param.arg_type))
                elif param.category == Parameter.IN_OUT:
                    self._write("%s: %s (INOUT)" % (param.name, param.arg_type))
                elif param.category == Parameter.OUT:
                    self._write("%s (OUT)" % param.arg_type)
            self._dedent()
        self._dedent()
                
    def _absname(self, basename):

        if not self._module_path:
            return basename
        else:
            return "::".join(self._module_path) + '::' + basename
        
    def _write(self, text):
        
        print(self._indent_level * " " + text)
        
    def _indent(self):
        
        self._indent_level += 4
        
    def _dedent(self):
        
        self._indent_level -= 4
        if self._indent_level < 0:
            self._indent_level = 0
                 
if __name__ == "__main__":
    
    unittest.main()

