from gobjcreator3.codegen.code_generator import CodeGenerator
from gobjcreator3.model.visibility import Visibility
import os
import fabscript

class CCodeGenerator(CodeGenerator):
    
    def __init__(self, root_module, origin):
        
        CodeGenerator.__init__(self, root_module, origin)
        
        self._dir_stack = []
        self._cur_dir = ""
        
        self._name_creator = NameCreator()
        self._refresh_template_processor()
                
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
            
        self._refresh_template_processor()
        self._setup_module_symbols(module)
        
        objs = [obj for obj in module.objects if obj.filepath_origin == self._origin]
        
        for obj in objs:
            self._setup_gobject_symbols(obj)
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
        lines = self._get_lines_from_template("gobject_header.template")
                
        self._out.visit_text_file(file_path, lines)
            
    def _gen_object_source(self, obj):
        
        file_path = self._cur_dir + os.sep + self._name_creator.create_obj_source_name(obj)
        lines = []
        
        self._out.visit_text_file(file_path, lines)
        
    def _get_lines_from_template(self, template_file):
        
        template_path = os.path.dirname(__file__) + os.sep + "templates" + os.sep + "c"
        template_path += os.sep + template_file
        template_path = os.path.abspath(template_path)
        
        out_buffer = self._template_processor.createStringOut()
        self._template_processor.createCode(template_path, out_buffer)
        
        return out_buffer.content.split(os.linesep)
        
    def _refresh_template_processor(self):
        
        self._template_processor = fabscript.API()
        self._template_processor.setEditableSectionStyle(self._template_processor.Language.C)

        self._template_processor["PUBLIC"] = Visibility.PUBLIC
        self._template_processor["PROTECTED"] = Visibility.PROTECTED
        self._template_processor["PRIVATE"] = Visibility.PRIVATE
        
    def _setup_module_symbols(self, module):
        
        camel_case_prefix = module.name.capitalize()
        curmod = module
        while curmod.module:
            curmod = curmod.module
            if curmod.name:
                camel_case_prefix = curmod.name.capitalize() + camel_case_prefix
                
        prefix = self._name_creator.replace_camel_case(camel_case_prefix, "_")
                    
        self._template_processor["module_prefix"] = prefix.lower()
        self._template_processor["MODULE_PREFIX"] = prefix.upper() 
        self._template_processor["ModulePrefix"] = camel_case_prefix
        self._template_processor["has_module"] = bool(module.name)
        
    def _setup_gobject_symbols(self, obj):
        
        self._template_processor["class"] = obj
        self._template_processor["ClassName"] = obj.name
        self._template_processor["CLASS_NAME"] = self._name_creator.replace_camel_case(obj.name, "_").upper()
        prefix = obj.cfunc_prefix or self._name_creator.replace_camel_case(obj.name, "_").lower()
        self._template_processor["class_prefix"] = prefix
        
class NameCreator(object):
    
    def __init__(self):
        
        self._file_name_sep = "-"

    def replace_camel_case(self, text, replace_char="_"):
        
        res = ""
        
        prev = None
        for ch in text:
            if prev and prev.lower() == prev and ch.lower() != ch:
                res += replace_char
            res += ch
            prev = ch
            
        return res
    
    def create_obj_header_name(self, obj):
        
        return self._create_elem_base_name(obj) + ".h"

    def create_obj_source_name(self, obj):
        
        return self._create_elem_base_name(obj) + ".c"
        
    def _create_elem_base_name(self, module_elem):
        
        res = self.replace_camel_case(module_elem.name, self._file_name_sep)
        
        module = module_elem.module
        while module and module.name:
            res = module.name + self._file_name_sep + res
            module = module.module
            
        res = res.lower()
        
        return res 
