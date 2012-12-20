from gobjcreator3.codegen.code_generator import CodeGenerator
from gobjcreator3.model.visibility import Visibility
from gobjcreator3.model.type import Type, BuiltIn, Reference, List
from gobjcreator3.model.method import Parameter
import os
import re
import fabscript

class CCodeGenerator(CodeGenerator):
    
    def __init__(self, root_module, origin):
        
        CodeGenerator.__init__(self, root_module, origin)
        
        self._dir_stack = []
        self._cur_dir = ""
        
        self._name_creator = NameCreator()
        self._refresh_template_processor()
        
        self._regex_type_w_ptrs = re.compile(r"(\w+)(\s*)(\*+)") 
                
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
            self._gen_object_prot_header(obj)
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
        
    def _gen_object_prot_header(self, obj):
        
        if not obj.has_protected_members() and not obj.is_abstract:
            return
            
        file_path = self._cur_dir + os.sep + self._name_creator.create_obj_prot_header_name(obj)
        lines = self._get_lines_from_template("gobject_header_prot.template")
        
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
        
        self._template_processor["TRUE"] = True
        self._template_processor["FALSE"] = False
        self._template_processor["PUBLIC"] = Visibility.PUBLIC
        self._template_processor["PROTECTED"] = Visibility.PROTECTED
        self._template_processor["PRIVATE"] = Visibility.PRIVATE
        self._template_processor["type_name"] = self._name_creator.create_full_type_name
        self._template_processor["is_empty"] = self._is_empty
        self._template_processor["rearrange_asterisk"] = self._rearrange_asterisk
        
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
                
    def _setup_gobject_symbols(self, obj):
        
        self._template_processor["class"] = obj
        self._template_processor["ClassName"] = obj.name
        self._template_processor["CLASS_NAME"] = self._name_creator.replace_camel_case(obj.name, "_").upper()
        self._template_processor["FullClassName"] = self._template_processor.getSymbol("ModulePrefix") + obj.name
        
        prefix = obj.cfunc_prefix or self._name_creator.replace_camel_case(obj.name, "_").lower()
        module_prefix = self._template_processor.getSymbol("module_prefix")
        if module_prefix:
            prefix = module_prefix + "_" + prefix
        self._template_processor["class_prefix"] = prefix
        
        self._template_processor["protected_header"] = self._name_creator.create_obj_prot_header_name
        self._template_processor["filename_wo_suffix"] = self._name_creator.create_filename_wo_suffix
        
        self._template_processor["method_result"] = self._method_result
        self._template_processor["method_signature"] = self._method_signature
        
        self._template_processor["hasProtectedMembers"] = obj.has_protected_members()
        
    def _is_empty(self, data):
        
        return bool(data) == False
    
    def _method_result(self, method):
        
        result_type = "void"
        
        for p in method.parameters:
            type_name = self._name_creator.create_full_type_name(p.type)
            if isinstance(p.type, Type) and ( p.type.category == Type.OBJECT or p.type.category == Type.INTERFACE ):
                type_name += "*"
            if "const" in p.modifiers:
                type_name = "const " + type_name
            if p.direction == Parameter.OUT:
                result_type = type_name
                break
            
        return self._rearrange_asterisk(result_type)
            
    def _method_signature(self, 
                          cls,
                          method,
                          suppress_param_names=False,
                          insert_line_breaks=True,
                          indent_level=1
                          ):
        
        res = ""
        
        params = []
        for p in method.parameters:
            type_name = self._name_creator.create_full_type_name(p.type)
            if isinstance(p.type, Type) and ( p.type.category == Type.OBJECT or p.type.category == Type.INTERFACE ):
                type_name += "*"
            if "const" in p.modifiers:
                type_name = "const " + type_name
            if p.direction != Parameter.OUT:
                params.append((type_name, p.name))
                
        if not method.is_static:
            cls_type = self._name_creator.create_full_type_name(cls) 
            params.insert(0, (cls_type + "*", "self"))
            
        if len(params) == 0:
            
            res = "void"
                        
        elif len(params) == 1:
            
            res = params[0][0]
            if not suppress_param_names:
                res = self._rearrange_asterisk(res, params[0][1])
        
        else:    
            
            for param in params:
                if res:
                    res += ", " 
                if insert_line_breaks:
                    res += "\n"
                    res += indent_level * "\t"
                typename = param[0]
                if not suppress_param_names:
                    res += self._rearrange_asterisk(typename, param[1])
                else:
                    res += typename 

            if insert_line_breaks:
                res += "\n"
                res += indent_level * "\t"
                
        return res
    
    def _rearrange_asterisk(self, typename, parname=None):
        
        match = self._regex_type_w_ptrs.match(typename)
        if match:
            if parname:
                typename = match.group(1)
                parname = match.group(3) + parname
            else:
                typename = match.group(1) + " " + match.group(3)

        if parname:            
            return typename + " " + parname
        else:
            return typename
                
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
    
    def create_filename_wo_suffix(self, elem):
        
        return self._create_elem_base_name(elem)
    
    def create_obj_header_name(self, obj):
        
        return self._create_elem_base_name(obj) + ".h"

    def create_obj_prot_header_name(self, obj):
        
        return self._create_elem_base_name(obj) + self._file_name_sep + "protected.h"

    def create_obj_source_name(self, obj):
        
        return self._create_elem_base_name(obj) + ".c"

    def create_full_type_name(self, type_, with_asterisk=False):
        
        if isinstance(type_, Reference):
            res = self.create_full_type_name(type_.target_type) + "*"
        elif isinstance(type_, List):
            res = self.create_full_type_name(type_.line_type) + "*"
        elif isinstance(type_, BuiltIn):
            res = {"string" : "gchar*",
                   "boolean": "gboolean",
                   "integer": "gint",
                   "unsigned integer": "guint",
                   "float": "gfloat",
                   "double": "gdouble",
                   "any": "gpointer"
                   }[type_.name]
        else:
            res = type_.name
                        
            module = type_.module
            while module and module.name:
                res = module.name.capitalize() + res
                module = module.module
                
            if with_asterisk:
                if type_.category in [Type.OBJECT, Type.INTERFACE]:
                    res += "*"
        
        return res
        
    def _create_elem_base_name(self, module_elem):
        
        res = self.replace_camel_case(module_elem.name, self._file_name_sep)
        
        module = module_elem.module
        while module and module.name:
            res = module.name + self._file_name_sep + res
            module = module.module
            
        res = res.lower()
        
        return res 
