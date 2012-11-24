from gobjcreator3.ast_visitor import AstVisitor
from gobjcreator3.parser import GobjcreatorParser
from gobjcreator3.interpreter import Interpreter
from gobjcreator3.include_dirs import IncludeDirs

from gobjcreator3.model.module import RootModule, ModuleElement
from gobjcreator3.model.type import Type
from gobjcreator3.model.gobject import GObject

class CompileStep0(AstVisitor):
    
    def __init__(self, include_dirs = IncludeDirs()):
        
        AstVisitor.__init__(self)
        
        self._include_dirs = include_dirs
        self._search_path_std = []
        
        self._parser = GobjcreatorParser()
        self._interpreter = Interpreter()
        
    def process_file(self, filepath):
        
        self._file_stack = []
        self._push_file(filepath)
        
        self._syntax_trees = {}
        self._root_modules = {}

        self._process_current_file()
        
        return self._current_root
            
    def _process_current_file(self):
        
        filepath = self._file_stack[-1]
        
        if filepath in self._root_modules:
            return None
        
        if filepath in self._syntax_trees:
            ast = self._syntax_trees[filepath]
        else: 
            try:
                ast = self._parser.parseFile(filepath)
                self._syntax_trees[filepath] = ast
            except Exception as parser_error:
                raise parser_error
        
        self._current_root = RootModule()
        self._root_modules[filepath] = self._current_root
        self._module_stack = []
        self._object = None
                
        self._interpreter.eval_grammar(ast, self)
        
        return self._current_root
    
    def _push_file(self, filepath):
        
        self._file_stack.append(filepath)
        self._current_file = filepath
        
    def _pop_file(self):
        
        self._file_stack.pop()
        self._current_file = self._file_stack[-1]
        
    def _get_current_module(self):
        
        module_path = ModuleElement.MODULE_SEP.join(self._module_stack)
        return self._current_root.get_module(module_path)
        
    # AstVisitor interface:
                
    def enter_grammar(self):
        pass
    
    def exit_grammar(self):
        pass
    
    def visit_include_path(self, 
                           include_path,
                           is_standard_path
                           ):
        
        filepath = self._include_dirs.get_abs_filepath(
                                                       include_path, 
                                                       is_standard_path
                                                       )
        self._push_file(filepath)
        
        file_root = self._process_current_file()
        
        self._pop_file()
        
        self._current_root = self._root_modules[self._current_file]
        if file_root:
            self._current_root.merge(file_root)
            
    def enter_module(self, module_name):
        
        self._module_stack.append(module_name)
        
        module = self._get_current_module()
        module.filepath_origin = self._current_file
        
    def exit_module(self):
        
        self._module_stack.pop()
    
    def visit_type_declaration(self, typename):

        type_ = Type(typename)
        type_.filepath_origin = self._current_file
        
        module = self._get_current_module()
        module.add_type(type_)
        
    def enter_gobject(self, 
                      name,
                      super_class,
                      interfaces
                      ):
        
        self._object = GObject(name)
        self._object.filepath_origin = self._current_file
    
    def exit_gobject(self):
        
        self._get_current_module().add_object(self._object)
        self._object = None
    
    def enter_ginterface(self, name):
        pass
    
    def exit_ginterface(self):
        pass    
    
    def visit_gerror(self, name, codes):
        pass
    
    def visit_genum(self, name, codeNamesValues):
        pass
    
    def visit_gflags(self, name, codes):
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
        