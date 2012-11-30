from gobjcreator3.preprocessor import PreProcessor
from gobjcreator3.interpreter import Interpreter
from gobjcreator3.ast_visitor import AstVisitor
from gobjcreator3.parameter import FullTypeName, BuiltIn

from gobjcreator3.model.module import Module, RootModule, ModuleElement
from gobjcreator3.model.type import Type, BuiltIn as BuiltInType
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
        
        existing_module = parent.get_module(cur_module.name)
        if existing_module is None:
            parent.add_element(cur_module)
        else:
            existing_module.merge(cur_module)
    
    def visit_type_declaration(self, typename, origin):

        type_ = Type(typename, Type.OTHER)
        type_.filepath_origin = origin
        
        module = self._module_stack[-1]
        module.add_element(type_)
        
    def enter_gobject(self, 
                      name,
                      super_class,
                      interfaces,
                      origin
                      ):
        
        self._object = GObject(name)
        self._object.filepath_origin = origin 
    
    def exit_gobject(self):
        
        self._module_stack[-1].add_element(self._object)
        self._object = None
    
    def enter_ginterface(self, name, origin):
        
        self._interface = GInterface(name)
        self._interface.filepath_origin = origin
    
    def exit_ginterface(self):
        
        self._module_stack[-1].add_element(self._interface)
        self._interface = None
                
    def visit_gerror(self, name, codes, origin):
        
        error_domain = GError(name, codes)
        error_domain.filepath_origin = origin
        self._module_stack[-1].add_element(error_domain)
    
    def visit_genum(self, name, codeNamesValues, origin):
        
        enum = GEnum(name, codeNamesValues)
        enum.filepath_origin = origin
        self._module_stack[-1].add_element(enum)
            
    def visit_gflags(self, name, codes, origin):
        
        flags = GFlags(name, codes)
        flags.filepath_origin = origin
        self._module_stack[-1].add_element(flags)

class CompileStep1(AstVisitor):
    
    def __init__(self, root_module):
        
        self._root = root_module
        
    def _get_type(self, type_info):
        
        if isinstance(type_info, FullTypeName):
        
            path = ""
            for part in type_info.module_path:
                if path:
                    path += ModuleElement.MODULE_SEP
                path += part
                
            if path:
                path += ModuleElement.MODULE_SEP + type_info.name
            else:
                path = type_info.name 
                
            if not type_info.is_absolute_type:
                module = self._module_stack[-1]
            else:
                module = self._root
                
            return module.get_type_element(path)
                        
        elif isinstance(type_info, BuiltIn):
            
            return BuiltInType(type_info.name)
        
        else:
            
            raise Exception('Unsupported type!')
        
    # Visitor methods:
    
    def enter_grammar(self):
        
        self._module_stack = [self._root]
        self._gobject = None
        self._ginterface = None
    
    def exit_grammar(self):
        
        pass
    
    def enter_module(self, module_name, origin):
        
        module = self._module_stack[-1].get_module(module_name)
        self._module_stack.append(module)
            
    def exit_module(self):
        
        self._module_stack.pop()
    
    def enter_gobject(self, 
                      name,
                      super_class,
                      interfaces,
                      origin
                      ):
        
        cur_module = self._module_stack[-1]
        
        self._gobject = cur_module.get_object(name)
        
        if super_class:
            super = self._get_type(super_class)
            if super is None or super.category != Type.OBJECT:
                raise Exception("Super type '%s' does not exist or is not a class!" % super_class)
            self._gobject.super_class = super
        
        for intf_info in interfaces:
            intf = self._get_type(intf_info)
    
    def exit_gobject(self):

        self._gobject = None
    
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
    