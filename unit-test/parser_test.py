import unittest
import os
from gobjcreator3.preprocessor import PreProcessor
from gobjcreator3.interpreter import Interpreter
from gobjcreator3.ast_visitor import AstVisitor
from gobjcreator3.parameter import Parameter

_CURDIR = os.path.dirname(__file__)

class ParserTest(unittest.TestCase):
    
    def setUp(self):
        
        self._preprocessor = PreProcessor()
            
    def tearDown(self):
        
        self._preprocessor = None
        
    def testMyDemo(self):
        
        try:
            
            ast = self._preprocessor.get_expanded_ast(_CURDIR + os.sep + "mydemo.goc3")
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
 
    def enter_module(self, module_name, origin):
        
        self._write("Module: %s [from %s]" % (self._absname(module_name), origin))
        
        self._module_path.append(module_name)
        self._indent()
        
    def exit_module(self):
        
        self._module_path.pop()
        self._dedent()

    def visit_type_declaration(self, typename, origin):
        
        self._write("GType: %s [from %s]" % (self._absname(typename), origin))
                
    def enter_gobject(self, 
                      name,
                      super_class,
                      interfaces,
                      cfunc_prefix,
                      origin
                      ):
        
        if not super_class:
            self._write("GObject: %s [from %s]" % (self._absname(name), origin))
        else:
            self._write("GObject: %s > %s [from %s]" % (self._absname(name), super_class, origin))
        self._indent()
        
        if interfaces:
            self._write("Implements:")
            self._indent()
            for intf in interfaces:
                self._write(intf)
            self._dedent()
                
    def exit_gobject(self):
        
        self._dedent()

    def enter_ginterface(self, name, cfunc_prefix, origin):
        
        self._write("GInterface: %s [from %s]" % (self._absname(name), origin))
        self._indent()

    def exit_ginterface(self):
        
        self._dedent()

    def visit_gerror(self, name, codes, origin):
        
        self._write("GError: %s [from %s]" % (self._absname(name), origin))
        self._indent()
        for code in codes:
            self._write(code)
        self._dedent()

    def visit_genum(self, name, codeNamesValues, origin):
        
        self._write("GEnum: %s [from %s]" % (self._absname(name), origin))
        self._indent()
        for cname, cval in codeNamesValues:
            if cval is None:
                self._write(cname)
            else:
                self._write(cname + " = %s" % cval)
        self._dedent()

    def visit_gflags(self, name, codes, origin):
        
        self._write("GFlags: %s [from %s]" % (self._absname(name), origin))
        self._indent()
        for code in codes:
            self._write(code)
        self._dedent()

    def visit_method(self, name, attrs, parameters):

        self._write("Method: %s" % name)
        self._indent()
        self._write("Attributes: %s" % attrs)
        if parameters:
            self._write("Parameters:")
            self._indent()    
            for param in parameters:
                if param.category == Parameter.IN:
                    self._write("%s: %s (IN) %s" % (param.name, param.arg_type, param.properties))
                elif param.category == Parameter.IN_OUT:
                    self._write("%s: %s (INOUT) %s" % (param.name, param.arg_type, param.properties))
                elif param.category == Parameter.OUT:
                    self._write("%s (OUT) %s" % (param.arg_type, param.properties))
            self._dedent()
        self._dedent()
        
    def visit_interface_method(self, name, parameters):
        
        self._write("Method: %s" % name)
        self._indent()
        if parameters:
            self._write("Parameters:")
            self._indent()    
            for param in parameters:
                if param.category == Parameter.IN:
                    self._write("%s: %s (IN) %s" % (param.name, param.arg_type, param.properties))
                elif param.category == Parameter.IN_OUT:
                    self._write("%s: %s (INOUT) %s" % (param.name, param.arg_type, param.properties))
                elif param.category == Parameter.OUT:
                    self._write("%s (OUT) %s" % (param.arg_type, param.properties))
            self._dedent()
        self._dedent()
        
    def visit_attribute(self, aname, atype, aattributes):
        
        self._write("Attribute: %s (%s) %s" % (aname, atype, aattributes))
        
    def visit_property(self, name, attributes):
        
        self._write("Property: %s %s" % (name, attributes))
        
    def visit_signal(self, name, parameters):
        
        self._write("Signal: %s" % name)
        self._indent()
        if parameters:
            self._write("Parameters:")
            self._indent()    
            for param in parameters:
                self._write("%s: %s %s" % (param.name, param.arg_type, param.properties))
            self._dedent()
        self._dedent()
                            
    def _absname(self, basename):

        if not self._module_path:
            return basename
        else:
            return "::".join(self._module_path) + '::' + basename
        
    def _write(self, text):
        
        print(self._indent_level * " " + str(text))
        
    def _indent(self):
        
        self._indent_level += 4
        
    def _dedent(self):
        
        self._indent_level -= 4
        if self._indent_level < 0:
            self._indent_level = 0
                 
if __name__ == "__main__":
    
    unittest.main()

