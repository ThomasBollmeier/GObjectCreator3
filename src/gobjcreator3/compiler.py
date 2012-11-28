from gobjcreator3.preprocessor import PreProcessor
from gobjcreator3.interpreter import Interpreter
from gobjcreator3.ast_visitor import AstVisitor

from gobjcreator3.model.module import Module, RootModule
from gobjcreator3.model.type import Type
from gobjcreator3.model.gobject import GObject
from gobjcreator3.model.ginterface import GInterface
from gobjcreator3.model.gerror import GError
from gobjcreator3.model.genum import GEnum
from gobjcreator3.model.gflags import GFlags

class Compiler(object):
    
    def __init__(self):
        
        self._preprocessor = PreProcessor()
        self._interpreter = Interpreter()
        
    def compile(self, filepath):
        
        expanded_ast = self._preprocessor.get_expanded_ast(filepath)
        
        step0 = CompileStep0()
        self._interpreter.eval_grammar(expanded_ast, step0)
        root_module = step0.get_root_module()
        
        step1 = CompileStep1(root_module)
        self._interpreter.eval_grammar(expanded_ast, step1)
                
        return root_module

class CompileStep0(AstVisitor):
    
    def __init__(self):
        
        AstVisitor.__init__(self)
        
        self._module_stack = []
                
    def get_root_module(self):
        
        return self._module_stack and self._module_stack[0] or None
        
    # AstVisitor interface:
                
    def enter_grammar(self):
        
        self._module_stack = [RootModule()]
        self._gobject = None
        self._ginterface = None
    
    def exit_grammar(self):
        
        pass
    
    def enter_module(self, module_name, origin):
        
        module = Module(module_name)
        module.filepath_origin = origin
        
        self._module_stack.append(module)
                
    def exit_module(self):
        
        cur_module = self._module_stack.pop()
        parent = self._module_stack[-1]
        parent.add_module(cur_module)
    
    def visit_type_declaration(self, typename, origin):

        type_ = Type(typename)
        type_.filepath_origin = origin
        
        module = self._module_stack[-1]
        module.add_type(type_)
        
    def enter_gobject(self, 
                      name,
                      super_class,
                      interfaces,
                      origin
                      ):
        
        self._object = GObject(name)
        self._object.filepath_origin = origin 
    
    def exit_gobject(self):
        
        self._module_stack[-1].add_object(self._object)
        self._object = None
    
    def enter_ginterface(self, name, origin):
        
        self._interface = GInterface(name)
        self._interface.filepath_origin = origin
    
    def exit_ginterface(self):
        
        self._module_stack[-1].add_interface(self._interface)
        self._interface = None
                
    def visit_gerror(self, name, codes, origin):
        
        error_domain = GError(name, codes)
        error_domain.filepath_origin = origin
        self._module_stack[-1].add_error_domain(error_domain)
    
    def visit_genum(self, name, codeNamesValues, origin):
        
        enum = GEnum(name, codeNamesValues)
        enum.filepath_origin = origin
        self._module_stack[-1].add_enumeration(enum)
            
    def visit_gflags(self, name, codes, origin):
        
        flags = GFlags(name, codes)
        flags.filepath_origin = origin
        self._module_stack[-1].add_flags(flags)

class CompileStep1(AstVisitor):
    
    def __init__(self, root_module):
        
        self._root = root_module
    
    def enter_grammar(self):
        pass
    
    def exit_grammar(self):
        pass
    
    def enter_module(self, module_name, origin):
        pass
    
    def exit_module(self):
        pass
    
    def visit_type_declaration(self, typename, origin):
        pass

    def enter_gobject(self, 
                      name,
                      super_class,
                      interfaces,
                      origin
                      ):
        pass
    
    def exit_gobject(self):
        pass
    
    def enter_ginterface(self, name, origin):
        pass
    
    def exit_ginterface(self):
        pass    
    
    def visit_gerror(self, name, codes, origin):
        pass
    
    def visit_genum(self, name, codeNamesValues, origin):
        pass
    
    def visit_gflags(self, name, codes, origin):
        pass
    
    def visit_method(self, 
                     name, 
                     attributes,
                     parameters 
                     ):
        pass
    
    def visit_interface_method(self,
                               name,
                               parameters
                               ):
        pass
    
    def visit_attribute(self,
                        aname,
                        atype,
                        aattributes
                        ):
        pass
    
    def visit_property(self,
                       name,
                       attributes
                       ):
        
        pass
    
    def visit_signal(self,
                     name,
                     parameters
                     ):
        pass
    