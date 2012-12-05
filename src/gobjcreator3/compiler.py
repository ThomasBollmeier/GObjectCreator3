from gobjcreator3.preprocessor import PreProcessor
from gobjcreator3.interpreter import Interpreter
from gobjcreator3.ast_visitor import AstVisitor
from gobjcreator3.parameter import FullTypeName, BuiltIn, RefTo, ListOf, Parameter as Param

from gobjcreator3.model.module import Module, RootModule, ModuleElement
from gobjcreator3.model.type import Type, BuiltIn as BuiltInType, Reference, List
from gobjcreator3.model.gobject import GObject
from gobjcreator3.model.ginterface import GInterface
from gobjcreator3.model.gerror import GError
from gobjcreator3.model.genum import GEnum
from gobjcreator3.model.gflags import GFlags
from gobjcreator3.model.property import Property, PropAccess, PropGTypeValue
from gobjcreator3.model.method import Method, Parameter
from gobjcreator3.model.attribute import Attribute
from gobjcreator3.model.visibility import Visibility

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
        
    def _get_param_type(self, arg_type):
        
        if  isinstance(arg_type, BuiltIn) or \
            isinstance(arg_type, FullTypeName):
            
            res = self._get_type(arg_type)
            if res is None:
                raise Exception("Unknown type '%s'" % arg_type)
            
            return res
        
        elif isinstance(arg_type, RefTo):
            
            target_type = self._get_param_type(arg_type.ref_type)
            
            return Reference(target_type)
        
        elif isinstance(arg_type, ListOf):
            
            line_type = self._get_param_type(arg_type.element_type)
            
            return List(line_type)

        else:
            
            raise Exception('Unsupported type!')
        
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
        
    def _get_gtype(self, gtype_info):
        
        gtype_id = gtype_info.gtype_id
        if gtype_info.full_type_name:
            type_ = self._get_type(gtype_info.full_type_name)
                
        return PropGTypeValue(gtype_id, type_)
        
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
        
        self._gobject = self._module_stack[-1].get_object(name)
        
        if super_class:
            super = self._get_type(super_class)
            if super is None or super.category != Type.OBJECT:
                raise Exception("Super type '%s' does not exist or is not a class!" % super_class)
            self._gobject.super_class = super
        
        for intf_info in interfaces:
            intf = self._get_type(intf_info)
            if intf is None or intf.category != Type.INTERFACE:
                raise Exception("Interface type '%s' does not exist!" % intf_info)
            self._gobject.interfaces.append(intf)
    
    def exit_gobject(self):

        self._gobject = None
    
    def enter_ginterface(self, name, origin):
        
        self._ginterface = self._module_stack[-1].get_interface(name)
    
    def exit_ginterface(self):
        
        self._ginterface = None    
    
    def visit_method(self, 
                     name, 
                     attributes,
                     parameters 
                     ):
        
        if not attributes['overridden']:

            method = Method(name)

            method.visibility = attributes["visibility"]
            
            if attributes["static"]:
                method.set_static()
            
            if attributes["abstract"]:
                method.set_abstract()
            
            if attributes["final"]:
                method.set_final()
                
            method_params = []
            has_result = False
            for param in parameters:
                pname = param.name 
                ptype = self._get_param_type(param.arg_type)
                direction = {
                             Param.IN: Parameter.IN,
                             Param.OUT: Parameter.OUT,
                             Param.IN_OUT: Parameter.IN_OUT
                             }[param.category]
                if direction == Parameter.OUT:
                    if not has_result:
                        has_result = True
                    else:
                        raise Exception("Method '%s' must only have one result parameter!" % name)
                method_params.append(Parameter(pname, ptype, direction))
                
            method.parameters = method_params
            
            self._gobject.add_method(method)
            
        else:
            
            self._gobject.override(name)
    
    def visit_interface_method(self,
                               name,
                               parameters
                               ):
        
        method = Method(name)
        method.visibility = Visibility.PUBLIC
        method.set_abstract()
        
        self._ginterface.add_method(method)
    
    def visit_attribute(self,
                        aname,
                        atype,
                        aattributes
                        ):
        
        name = aname
        type_ = self._get_param_type(atype)
        visi = aattributes["visibility"]
        is_static = aattributes["static"]
        
        self._gobject.add_attribute(Attribute(name, type_, visi, is_static))
    
    def visit_property(self,
                       name,
                       attributes
                       ):
        
        pname = name
        try:
            ptype = attributes["type"]
        except:
            ptype = None
        try:
            access = attributes["access"]
        except:
            access = PropAccess.READ_ONLY
        try:
            description = attributes["description"]
        except:
            description = ""
        try:
            gtype = self._get_gtype(attributes["gtype"])
        except:
            gtype = None
        min_ = None
        max_ = None
        default = None
        try:
            auto_create = attributes["auto-create"]
        except:
            auto_create = False
        
        prop = Property(pname, 
                        ptype,
                        access,
                        description,
                        gtype,
                        min_,
                        max_,
                        default,
                        auto_create
                        )   
        
        self._gobject.add_property(prop)  
        
    def visit_signal(self,
                     name,
                     parameters
                     ):
        pass
    