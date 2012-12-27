from gobjcreator3.codegen.code_generator import CodeGenerator
from gobjcreator3.codegen.output import StdOut
from gobjcreator3.codegen.c_marshaller_generator import CMarshallerGenerator
from gobjcreator3.model.visibility import Visibility
from gobjcreator3.model.type import Type, BuiltIn, Reference, List
from gobjcreator3.model.method import Parameter
from gobjcreator3.model.property import PropType, PropAccess
import os
import re
import fabscript

class CCodeGenerator(CodeGenerator):
    
    def __init__(self, root_module, origin, out=StdOut()):
        
        CodeGenerator.__init__(self, root_module, origin, out)
        
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
            if obj.has_signals():
                self._gen_object_marshallers(obj)
            
        enums = [enum for enum in module.enumerations if enum.filepath_origin == self._origin]
        
        for enum in enums:
            self._setup_genum_symbols(enum)
            self._gen_enum_header(enum)
            self._gen_enum_source(enum)
                    
        self._out.exit_dir(self._cur_dir)

        self._dir_stack.pop()
        if self._dir_stack:
            self._cur_dir = self._dir_stack[-1]
        else:
            self._cur_dir = ""
        
    def _gen_object_header(self, obj):
        
        file_path = self._cur_dir + os.sep + self._name_creator.create_obj_header_name(obj)
        lines = self._get_lines_from_template("gobject_header.template", file_path)
                
        self._out.visit_text_file(file_path, lines)
        
    def _gen_object_prot_header(self, obj):
        
        if not obj.has_protected_members() and obj.is_final:
            return
            
        file_path = self._cur_dir + os.sep + self._name_creator.create_obj_prot_header_name(obj)
        lines = self._get_lines_from_template("gobject_header_prot.template", file_path)
        
        self._out.visit_text_file(file_path, lines)
            
    def _gen_object_source(self, obj):
        
        file_path = self._cur_dir + os.sep + self._name_creator.create_obj_source_name(obj)
        lines = self._get_lines_from_template("gobject_source.template", file_path)
        
        self._out.visit_text_file(file_path, lines)
        
    def _gen_object_marshallers(self, obj):
        
        header_guard = "__"
        modprefix = self._template_processor.getSymbol("MODULE_PREFIX")
        if modprefix:
            header_guard += modprefix + "_"
        header_guard += self._template_processor.getSymbol("CLASS_NAME")
        header_guard += "_MARSHALLER_H__"
        
        class_prefix = self._template_processor.getSymbol("class_prefix")
        signals = obj.get_signals()
        generator = CMarshallerGenerator(header_guard, class_prefix, signals, self._out)
        
        header_file_path = self._cur_dir + os.sep
        header_file_path += self._name_creator.create_obj_marshaller_header_name(obj)
        
        generator.generate_header(header_file_path)
        
        source_file_path = self._cur_dir + os.sep
        source_file_path += self._name_creator.create_obj_marshaller_source_name(obj)
        
        generator.generate_source(source_file_path)
        
    def _gen_enum_header(self, enum):
        
        file_path = self._cur_dir + os.sep + self._name_creator.create_filename_wo_suffix(enum) + ".h"
        lines = self._get_lines_from_template("genum_header.template", file_path)
        
        self._out.visit_text_file(file_path, lines)
                
    def _gen_enum_source(self, enum):
        
        file_path = self._cur_dir + os.sep + self._name_creator.create_filename_wo_suffix(enum) + ".c"
        lines = self._get_lines_from_template("genum_source.template", file_path)
        
        self._out.visit_text_file(file_path, lines)
                        
    def _get_lines_from_template(self, template_file, file_path):
        
        self._out.prepare_file_creation(file_path, self._template_processor)
        
        template_path = os.path.dirname(__file__) + os.sep + "templates" + os.sep + "c"
        template_path += os.sep + template_file
        template_path = os.path.abspath(template_path)
        
        out_buffer = self._template_processor.createStringOut()
        self._template_processor.createCode(template_path, out_buffer)
        
        lines = out_buffer.content.split(os.linesep)
        # Remove adjacent empty lines:
        res = []
        prev = None
        for line in lines:
            line = line.rstrip()
            if line:
                res.append(line)
            else:
                if prev is None or prev:
                    res.append(line)
            prev = line
        
        return res
        
    def _refresh_template_processor(self):
        
        self._template_processor = fabscript.API()
        self._template_processor.setEditableSectionStyle(self._template_processor.Language.C)
        
        self._template_processor["TRUE"] = True
        self._template_processor["FALSE"] = False
        self._template_processor["PUBLIC"] = Visibility.PUBLIC
        self._template_processor["PROTECTED"] = Visibility.PROTECTED
        self._template_processor["PRIVATE"] = Visibility.PRIVATE
        self._template_processor["type_name"] = self._name_creator.create_full_type_name
        self._template_processor["TYPE_MACRO"] = self._name_creator.create_type_macro
        self._template_processor["CAST_MACRO"] = self._name_creator.create_cast_macro
        self._template_processor["is_empty"] = self._is_empty
        self._template_processor["is_none"] = self._is_none
        self._template_processor["literal_trim"] = self._literal_trim
        self._template_processor["length"] = self._length
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
        self._template_processor["filename_wo_suffix"] = self._name_creator.create_filename_wo_suffix
                
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
        self._template_processor["marshaller_header"] = self._name_creator.create_obj_marshaller_header_name
        
        self._template_processor["method_result"] = self._method_result
        self._template_processor["method_signature"] = self._method_signature
        
        self._template_processor["hasProtectedMembers"] = obj.has_protected_members()
        
        self._template_processor["PROP_NAME"] = self._name_creator.create_property_enum_value
        self._template_processor["PropType"] = PropType
        self._template_processor["PropAccess"] = PropAccess
        self._template_processor["prop_value"] = self._property_value
        self._template_processor["prop_gtype"] = self._property_gtype
        self._template_processor["prop_flags"] = self._property_flags
        self._template_processor["prop_setter_section"] = self._property_setter_section
        self._template_processor["prop_getter_section"] = self._property_getter_section
        
        self._template_processor["signal_tech_name"] = self._signal_technical_name
        self._template_processor["signal_section_id"] = self._signal_section_id
        
    def _setup_genum_symbols(self, enum):
        
        self._template_processor["enum"] = enum
        self._template_processor["ENUM_NAME"] = self._name_creator.replace_camel_case(enum.name, "_").upper()
        self._template_processor["FullEnumName"] = self._template_processor.getSymbol("ModulePrefix") + enum.name
        
        prefix = self._name_creator.replace_camel_case(enum.name, "_").lower()
        module_prefix = self._template_processor.getSymbol("module_prefix")
        if module_prefix:
            prefix = module_prefix + "_" + prefix
        self._template_processor["enum_prefix"] = prefix
        
    def _is_empty(self, data):
        
        return bool(data) == False
    
    def _is_none(self, data):
        
        return data is None
    
    def _literal_trim(self, text):
        
        if len(text) > 2:
            return text[1:-1]
        else:
            return ""
        
    def _length(self, data):
        
        return len(data)
    
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
                          indent_level=1,
                          instance_name="self"
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
            params.insert(0, (cls_type + "*", instance_name))
            
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
    
    def _signal_technical_name(self, signal):
        
        return signal.name.replace("-", "_")
    
    def _signal_section_id(self, signal):
        
        return "signal_" + self._signal_technical_name(signal)
    
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
        
    def _property_flags(self, prop):
        
        flags = ""
        for access_mode in prop.access:
            if flags:
                flags += "|"
            flags += {
                      PropAccess.READ: "G_PARAM_READABLE",
                      PropAccess.WRITE: "G_PARAM_WRITABLE",
                      PropAccess.INIT: "G_PARAM_CONSTRUCT",
                      PropAccess.INIT_ONLY: "G_PARAM_CONSTRUCT_ONLY"
                      }[access_mode]
                
        return flags
                
    def _property_value(self, val):
        
        if val.literal:
            return val.literal
        elif val.number_info:
            if not val.number_info.decimals:
                return "%d" % val.number_info.digits
            else:
                return "%d.%d" % (val.number_info.digits, val.number_info.decimals)
        elif val.code_info:
            enum_name = self._name_creator.create_full_type_name(val.code_info.enumeration)
            enum_name = self._name_creator.replace_camel_case(enum_name, "_").upper()
            return enum_name + "_" + val.code_info.code_name
        elif val.boolean is not None:
            return val.boolean and "TRUE" or "FALSE"
        
    def _property_gtype(self, gtype_value):
        
        if gtype_value.gtype_id:
            return gtype_value.gtype_id
        else:
            return self._name_creator.create_type_macro(gtype_value.type)
        
    def _property_setter_section(self, prop):
        
        return "set_" + prop.name.replace("-", "_").lower()

    def _property_getter_section(self, prop):
        
        return "get_" + prop.name.replace("-", "_").lower()
                                        
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
    
    def create_obj_marshaller_header_name(self, obj):
        
        return self._create_elem_base_name(obj) + self._file_name_sep + "marshaller.h"

    def create_obj_marshaller_source_name(self, obj):
        
        return self._create_elem_base_name(obj) + self._file_name_sep + "marshaller.c"

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
    
    def create_type_macro(self, type_):
        
        basename = self.replace_camel_case(type_.name, "_").upper()

        module_prefix = ""
        module = type_.module
        while module and module.name:
            if module_prefix:
                module_prefix = module.name.upper() + "_" + module_prefix
            else:
                module_prefix = module.name.upper()
            module = module.module
        
        if module_prefix:
            return module_prefix + "_TYPE_" + basename
        else:
            return "TYPE_" + basename 

    def create_cast_macro(self, type_):
        
        basename = self.replace_camel_case(type_.name, "_").upper()

        module_prefix = ""
        module = type_.module
        while module and module.name:
            if module_prefix:
                module_prefix = module.name.upper() + "_" + module_prefix
            else:
                module_prefix = module.name.upper()
            module = module.module
        
        if module_prefix:
            return module_prefix + "_" + basename
        else:
            return basename 
        
    def create_property_enum_value(self, prop):
        
        underscore_name = prop.name.replace("-", "_")
        underscore_name = "PROP_" + underscore_name.upper()
        
        return underscore_name
        
    def _create_elem_base_name(self, module_elem):
        
        res = self.replace_camel_case(module_elem.name, self._file_name_sep)
        
        module = module_elem.module
        while module and module.name:
            res = module.name + self._file_name_sep + res
            module = module.module
            
        res = res.lower()
        
        return res 
