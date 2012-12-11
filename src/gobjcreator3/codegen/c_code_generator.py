from gobjcreator3.codegen.code_generator import CodeGenerator
import os

class CCodeGenerator(CodeGenerator):
    
    def __init__(self, root_module, origin):
        
        CodeGenerator.__init__(self, root_module, origin)
        
        self._dir_stack = []
        self._cur_dir = ""
        
        self._name_creator = NameCreator()
        
    def generate(self):
        
        self._generate_module(self._root_module)
        
    def _generate_module(self, module):
        
        if self._cur_dir:
            self._cur_dir += os.sep + module.name
        else:
            self._cur_dir = module.name
        self._dir_stack.append(self._cur_dir)
        
        self._out.enter_dir(self._cur_dir)
        
        for m in module.modules:
            self._generate_module(m)
        
        objs = [obj for obj in module.objects if obj.filepath_origin == self._origin]
        
        for obj in objs:
            self._gen_object_header(obj)
            self._gen_object_source(obj)
                    
        self._out.exit_dir(self._cur_dir)

        self._dir_stack.pop()
        if self._dir_stack:
            self._cur_dir = self._dir_stack[-1]
        else:
            self._cur_dir = ""
        
    def _gen_object_header(self, obj):
        
        file_path = self._cur_dir + os.sep + self._name_creator.create_obj_header_name(obj)
        lines = []
        
        self._out.visit_text_file(file_path, lines)
            
    def _gen_object_source(self, obj):
        
        file_path = self._cur_dir + os.sep + self._name_creator.create_obj_source_name(obj)
        lines = []
        
        self._out.visit_text_file(file_path, lines)
        
class NameCreator(object):
    
    def __init__(self):
        
        self._file_name_sep = "-"
    
    def create_obj_header_name(self, obj):
        
        return self._create_elem_base_name(obj) + ".h"

    def create_obj_source_name(self, obj):
        
        return self._create_elem_base_name(obj) + ".c"
        
    def _create_elem_base_name(self, module_elem):
        
        res = self._replace_camel_case(module_elem.name, self._file_name_sep)
        
        module = module_elem.module
        while module and module.name:
            res = module.name + self._file_name_sep + res
            module = module.module
            
        res = res.lower()
        
        return res 
    
    def _replace_camel_case(self, text, replace_char="_"):
        
        res = ""
        
        prev = None
        for ch in text:
            if prev and prev.lower() == prev and ch.lower() != ch:
                res += replace_char
            res += ch
            prev = ch
            
        return res
