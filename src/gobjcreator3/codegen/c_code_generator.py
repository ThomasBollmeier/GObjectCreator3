from gobjcreator3.codegen.code_generator import CodeGenerator
from gobjcreator3.codegen.output import StdOut
from gobjcreator3.codegen.name_creator import NameCreator
from gobjcreator3.codegen.c_marshaller_generator import CMarshallerGenerator, CMarshallerNameCreator
from gobjcreator3.model.type import Type
from gobjcreator3.model.visibility import Visibility
from gobjcreator3.model.method import Parameter
from gobjcreator3.model.property import PropType, PropAccess
from gobjcreator3.model.ginterface import GInterface
from gobjcreator3.introspection import Transfer, OutAlloc
import os
import re
import faberscriptorum

class CGenConfig(object):
    
    def __init__(self):
        
        self.generate_base_functions = False
        self.generate_constructor = False
        self.generate_setter_getter = False
        self.verbose = False
        self.header_text_file = "" 
        self.directory_per_module = True
        
class CCodeGenerator(CodeGenerator):
    
    def __init__(self, root_module, origin, out=StdOut(), config=CGenConfig()):
        
        CodeGenerator.__init__(self, root_module, origin, out)
        
        self._config = config
        
        self._dir_stack = []
        self._cur_dir = ""
        
        self._name_creator = NameCreator()
        
        self._template_dir = os.path.dirname(__file__) + os.sep + "templates" + os.sep + "c"
        self._refresh_template_processor()
        
        self._regex_type_w_ptrs = re.compile(r"(\w+)(\s*)(\*+)")
                
    def generate(self):
        
        self._generate_module(self._root_module)
        
    def _generate_module(self, module):
        
        if self._config.directory_per_module:
            
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

        intfs = [intf for intf in module.interfaces if intf.filepath_origin == self._origin]
        
        for intf in intfs:
            self._setup_ginterface_symbols(intf)
            self._gen_interface_header(intf)
            self._gen_interface_source(intf)
            if intf.signals:
                self._gen_object_marshallers(intf)
            
        enums = [enum for enum in module.enumerations if enum.filepath_origin == self._origin]
        
        for enum in enums:
            self._setup_genum_symbols(enum)
            self._gen_enum_header(enum)
            self._gen_enum_source(enum)

        all_flags = [flags for flags in module.flags if flags.filepath_origin == self._origin]
        
        for flags in all_flags:
            self._setup_gflags_symbols(flags)
            self._gen_flags_header(flags)
            self._gen_flags_source(flags)
            
        error_domains = [error_domain for error_domain in module.error_domains if error_domain.filepath_origin == self._origin]
        
        for error_domain in error_domains:
            self._setup_gerror_symbols(error_domain)
            self._gen_error_header(error_domain)
            
        if self._config.directory_per_module:
                                
            self._out.exit_dir(self._cur_dir)

            self._dir_stack.pop()
            if self._dir_stack:
                self._cur_dir = self._dir_stack[-1]
            else:
                self._cur_dir = ""
        
    def _gen_object_header(self, obj):
        
        file_path = self._full_path(self._name_creator.create_obj_header_name(obj))
        lines = self._get_lines_from_template("gobject_header.template", file_path)
                
        self._create_text_file(file_path, lines)
        
    def _gen_object_prot_header(self, obj):
        
        if not obj.has_protected_members() and obj.is_final:
            return
            
        file_path = self._full_path(self._name_creator.create_obj_prot_header_name(obj))
        lines = self._get_lines_from_template("gobject_header_prot.template", file_path)
        
        self._create_text_file(file_path, lines)
            
    def _gen_object_source(self, obj):
        
        file_path = self._full_path(self._name_creator.create_obj_source_name(obj))
        lines = self._get_lines_from_template("gobject_source.template", file_path)
        
        self._create_text_file(file_path, lines)
        
    def _gen_interface_header(self, intf):
        
        file_path = self._full_path(self._name_creator.create_obj_header_name(intf))
        lines = self._get_lines_from_template("ginterface_header.template", file_path)
                
        self._create_text_file(file_path, lines)

    def _gen_interface_source(self, intf):
        
        file_path = self._full_path(self._name_creator.create_obj_source_name(intf))
        lines = self._get_lines_from_template("ginterface_source.template", file_path)
                
        self._create_text_file(file_path, lines)
        
    def _gen_object_marshallers(self, clif):
        
        is_interface = isinstance(clif, GInterface)
        
        header_guard = "__"
        modprefix = self._template_processor.getSymbol("MODULE_PREFIX")
        if modprefix:
            header_guard += modprefix + "_"
        if not is_interface:
            header_guard += self._template_processor.getSymbol("CLASS_NAME")
        else:
            header_guard += self._template_processor.getSymbol("INTF_NAME")
        header_guard += "_MARSHALLER_H__"
        
        if not is_interface:
            prefix = self._template_processor.getSymbol("class_prefix")
        else:
            prefix = self._template_processor.getSymbol("intf_prefix")
        signals = clif.get_signals()
        generator = CMarshallerGenerator(
                                         self._header_comment(),
                                         header_guard,
                                         prefix,
                                         signals, 
                                         self._out
                                         )
        
        header_file_path = self._full_path(self._name_creator.create_obj_marshaller_header_name(clif))

        if self._config.verbose:
            print("generating %s..." % header_file_path, end="")
        
        generator.generate_header(header_file_path)

        if self._config.verbose:
            print("done")

        source_file_path = self._full_path(self._name_creator.create_obj_marshaller_source_name(clif))

        if self._config.verbose:
            print("generating %s..." % source_file_path, end="")
        
        generator.generate_source(source_file_path)

        if self._config.verbose:
            print("done")
        
    def _gen_enum_header(self, enum):
        
        file_path = self._full_path(self._name_creator.create_filename_wo_suffix(enum) + ".h")
        lines = self._get_lines_from_template("genum_header.template", file_path)
        
        self._create_text_file(file_path, lines)
                
    def _gen_enum_source(self, enum):
        
        file_path = self._full_path(self._name_creator.create_filename_wo_suffix(enum) + ".c")
        lines = self._get_lines_from_template("genum_source.template", file_path)
        
        self._create_text_file(file_path, lines)

    def _gen_flags_header(self, flags):
        
        file_path = self._full_path(self._name_creator.create_filename_wo_suffix(flags) + ".h")
        lines = self._get_lines_from_template("gflags_header.template", file_path)
        
        self._create_text_file(file_path, lines)

    def _gen_flags_source(self, flags):
        
        file_path = self._full_path(self._name_creator.create_filename_wo_suffix(flags) + ".c")
        lines = self._get_lines_from_template("gflags_source.template", file_path)
        
        self._create_text_file(file_path, lines)

    def _gen_error_header(self, error_domain):
        
        file_path = self._full_path(self._name_creator.create_filename_wo_suffix(error_domain) + ".h")
        lines = self._get_lines_from_template("gerror_header.template", file_path)
        
        self._create_text_file(file_path, lines)
        
    def _full_path(self, basename):
        
        if self._cur_dir:
            return self._cur_dir + os.sep + basename
        else:
            return basename
        
    def _create_text_file(self, file_path, lines):
        
        if self._config.verbose:
            print("generating %s..." % file_path, end="")
        
        self._out.visit_text_file(file_path, lines)
        
        if self._config.verbose:
            print("done")
                        
    def _get_lines_from_template(self, template_file, file_path):
        
        self._out.prepare_file_creation(file_path, self._template_processor)
        
        template_path = self._template_dir + os.sep + template_file
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
        
        self._template_processor = faberscriptorum.API()
        self._template_processor.setEditableSectionStyle(self._template_processor.Language.C)
        self._template_processor.setIncludePath([self._template_dir])
                
        self._template_processor["header_comment"] = self._header_comment()
        self._template_processor["config"] = self._config
        self._template_processor["TRUE"] = True
        self._template_processor["FALSE"] = False
        self._template_processor["PUBLIC"] = Visibility.PUBLIC
        self._template_processor["PROTECTED"] = Visibility.PROTECTED
        self._template_processor["PRIVATE"] = Visibility.PRIVATE
        self._template_processor["OBJECT"] = Type.OBJECT
        self._template_processor["INTERFACE"] = Type.INTERFACE
        self._template_processor["type_name"] = self._name_creator.create_full_type_name
        self._template_processor["TYPE_MACRO"] = self._name_creator.create_type_macro
        self._template_processor["CAST_MACRO"] = self._name_creator.create_cast_macro
        self._template_processor["increment"] = self._increment
        self._template_processor["is_empty"] = self._is_empty
        self._template_processor["is_none"] = self._is_none
        self._template_processor["literal_trim"] = self._literal_trim
        self._template_processor["length"] = self._length
        self._template_processor["to_upper"] = self._to_upper
        self._template_processor["to_lower"] = self._to_lower
        self._template_processor["rearrange_asterisk"] = self._rearrange_asterisk

        self._template_processor["method_basename"] = self._method_basename
        self._template_processor["method_result"] = self._method_result
        self._template_processor["method_signature"] = self._method_signature
        self._template_processor["method_signature_by_name"] = self._method_signature_by_name
        self._template_processor["method_by_name"] = self._method_by_name
        self._template_processor["method_call_args"] = self._method_call_args
        self._template_processor["method_def_class"] = self._method_def_class
        self._template_processor["method_def_class_cast"] = self._method_def_class_cast
        
        self._template_processor["IN"] = Parameter.IN
        self._template_processor["IN_OUT"] = Parameter.IN_OUT
        self._template_processor["OUT"] = Parameter.OUT
        self._template_processor["introspec_param_info"] = self._introspec_param_info
                
    def _setup_module_symbols(self, module):
        
        camel_case_prefix = module.name.capitalize()
        curmod = module
        while curmod.module:
            curmod = curmod.module
            if curmod.name:
                camel_case_prefix = curmod.name.capitalize() + camel_case_prefix
                
        prefix = self._name_creator.replace_camel_case(camel_case_prefix, "_")
                    
        self._template_processor["module_prefix"] = self._module_prefix(module)
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

        self._template_processor["hasProtectedMembers"] = obj.has_protected_members()
        
        self._template_processor["PROP_NAME"] = self._name_creator.create_property_enum_value
        self._template_processor["prop_tech_name"] = self._name_creator.create_property_tech_name
        self._template_processor["PropType"] = PropType
        self._template_processor["PropAccess"] = PropAccess
        self._template_processor["prop_value"] = self._property_value
        self._template_processor["prop_gtype"] = self._property_gtype
        self._template_processor["prop_flags"] = self._property_flags
        self._template_processor["prop_setter_section"] = self._property_setter_section
        self._template_processor["prop_getter_section"] = self._property_getter_section
        self._template_processor["prop_set_section"] = self._property_setter_section
        self._template_processor["prop_get_section"] = self._property_getter_section
        self._template_processor["is_prop_init_required"] = self._is_property_init_required
        
        self._template_processor["signal_tech_name"] = self._signal_technical_name
        self._template_processor["signal_section_defhandler"] = self._signal_section_defhandler
        
        if obj.has_signals():
            self._marshaller_names = CMarshallerNameCreator(prefix)
            self._template_processor["marshaller_func"] = self._marshaller_names.create_marshaller_name
        else:
            self._marshaller_names = None
            
        self._template_processor["interface_impl_funcname"] = self._interface_impl_funcname
            
    def _setup_ginterface_symbols(self, intf):
        
        self._template_processor["intf"] = intf
        self._template_processor["INTF_NAME"] = self._name_creator.replace_camel_case(intf.name, "_").upper()
        
        prefix = intf.cfunc_prefix or self._name_creator.replace_camel_case(intf.name, "_").lower()
        module_prefix = self._template_processor.getSymbol("module_prefix")
        if module_prefix:
            prefix = module_prefix + "_" + prefix
        self._template_processor["intf_prefix"] = prefix

        if intf.signals:
            self._marshaller_names = CMarshallerNameCreator(prefix)
            self._template_processor["marshaller_func"] = self._marshaller_names.create_marshaller_name
        else:
            self._marshaller_names = None
        
    def _setup_genum_symbols(self, enum):
        
        self._template_processor["enum"] = enum
        self._template_processor["ENUM_NAME"] = self._name_creator.replace_camel_case(enum.name, "_").upper()
        self._template_processor["FullEnumName"] = self._template_processor.getSymbol("ModulePrefix") + enum.name
        
        prefix = self._name_creator.replace_camel_case(enum.name, "_").lower()
        module_prefix = self._template_processor.getSymbol("module_prefix")
        if module_prefix:
            prefix = module_prefix + "_" + prefix
        self._template_processor["enum_prefix"] = prefix

    def _setup_gflags_symbols(self, flags):
        
        self._template_processor["flags"] = flags
        
        prefix = self._name_creator.replace_camel_case(flags.name, "_").lower()
        module_prefix = self._template_processor.getSymbol("module_prefix")
        if module_prefix:
            prefix = module_prefix + "_" + prefix
        self._template_processor["flags_prefix"] = prefix
        
    def _setup_gerror_symbols(self, error_domain):
        
        self._template_processor["error_domain"] = error_domain

        prefix = self._name_creator.replace_camel_case(error_domain.name, "_").lower()
        module_prefix = self._template_processor.getSymbol("module_prefix")
        if module_prefix:
            prefix = module_prefix + "_" + prefix
        self._template_processor["error_domain_prefix"] = prefix
        
    def _header_comment(self):
        
        if not self._config.header_text_file:
            
            return """/*
 * This file has been automatically generated by GObjectCreator3
 * (see https://github.com/ThomasBollmeier/GObjectCreator3 for details)
 */        
"""
        else:
            
            res = ""
            
            f = open(self._config.header_text_file)
            lines = f.readlines()
            f.close
            for line in lines:
                res += line
                
            return res
        
    def _increment(self, value):
        
        return value + 1
    
    def _introspec_param_info(self, param):
        
        ispec_data = param.ispec_data
        
        if param.direction == Parameter.IN:
            res = "(in)"
        elif param.direction == Parameter.IN_OUT:
            res = "(inout)"
        elif param.direction == Parameter.OUT:
            if ispec_data is None or ispec_data.out_alloc is None:
                res = "(out)"
            else:
                if ispec_data.out_alloc == OutAlloc.CALLEE:
                    res = "(out callee-allocates)"
                elif ispec_data.out_alloc == OutAlloc.CALLER:
                    res = "(out caller-allocates)"
                else:
                    res = "(out)"
                    
        if ispec_data is None:
            return res
        
        if ispec_data.transfer is not None:
            res += " "
            res += {
                    Transfer.NONE: "(transfer none)",
                    Transfer.FULL: "(transfer full)",
                    Transfer.CONTAINER: "(transfer container)"
                    }[ispec_data.transfer]
                    
        if ispec_data.allow_none is not None:
            res += " "
            if ispec_data.allow_none:
                res += "(allow-none)"
        
        return res
                
    def _is_empty(self, data):
        
        return bool(data) == False
    
    def _is_none(self, data):
        
        return data is None
    
    def _to_upper(self, text):
        
        return text.upper()

    def _to_lower(self, text):
        
        return text.lower()
    
    def _literal_trim(self, text):
        
        if len(text) > 2:
            return text[1:-1]
        else:
            return ""
        
    def _length(self, data):
        
        try:
            return len(data)
        except TypeError as error:
            raise error
    
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
    
    def _method_basename(self,
                         cls,
                         method_info
                         ):
        
        method_or_name, intf = method_info
        
        if not isinstance(method_or_name, str):
            res = method_or_name.name
        else:
            res = method_or_name
        
        if intf:
            method_prefix = intf.cfunc_prefix or intf.name.lower()
            mod_prefix = self._module_prefix_relative(intf.module, cls.module)
            if mod_prefix:
                method_prefix = mod_prefix + "_" + method_prefix 
            res = method_prefix + "_" + res 
        
        return res
                    
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
    
    def _method_call_args(self, 
                          method, 
                          insert_line_breaks = True, 
                          indent_level = 1, 
                          instance_name = "self"
                          ):
        
        args = [p.name for p in method.parameters if p.direction != Parameter.OUT]
        
        if not method.is_static:
            args.insert(0, instance_name)
            
        num_args = len(args)
        if num_args == 0:
            res = ""
        elif num_args == 1:
            res = args[0]
        else:
            res = ""
            for arg in args: 
                if res:
                    res += ","
                if insert_line_breaks:
                    res += "\n"
                    res += indent_level * "\t"
                res += arg
            if insert_line_breaks:
                res += "\n"
                res += indent_level * "\t"
            
        return res
    
    def _method_signature_by_name(self,
                                  cls, 
                                  method_name, 
                                  suppress_param_names=False,
                                  insert_line_breaks=True,
                                  indent_level=1,
                                  instance_name="self"
                                  ):
        
        minfo = cls.get_method_info(method_name)
        
        return self._method_signature(
                                      minfo.def_origin, 
                                      minfo.method, 
                                      suppress_param_names, 
                                      insert_line_breaks, 
                                      indent_level, 
                                      instance_name
                                      )
        
    def _method_by_name(self, cls, method_name, intf=None):
        
        minfo = cls.get_method_info(method_name, intf)
        
        return minfo.method
    
    def _method_def_class(self, cls, method_name, intf=None):

        minfo = cls.get_method_info(method_name, intf)
        
        if minfo:
            return minfo.def_origin
        else:
            raise Exception("No class found for method '%s'" % method_name)
                
    def _method_def_class_cast(self, cls, method_name, intf=None):
        
        minfo = cls.get_method_info(method_name, intf)
        
        defcls = minfo.def_origin
        class_name = self._name_creator.replace_camel_case(defcls.name, "_").upper()
                
        module_prefix = ""
        module = defcls.module
        while module and module.name:
            if module_prefix:
                module_prefix = "_" + module_prefix
            module_prefix = module.name.upper() + module_prefix
            module = module.module
            
        res = class_name + "_CLASS"
            
        if module_prefix:
            res = module_prefix + "_" + res

        return res 
    
    def _signal_technical_name(self, signal):
        
        return signal.name.replace("-", "_")
    
    def _signal_section_defhandler(self, signal):
        
        return "default_handler_" + self._signal_technical_name(signal)
    
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
        
        return "setter_" + prop.name.replace("-", "_").lower()

    def _property_getter_section(self, prop):
        
        return "getter_" + prop.name.replace("-", "_").lower()

    def _property_set_section(self, prop):
        
        return "set_" + prop.name.replace("-", "_").lower()

    def _property_get_section(self, prop):
        
        return "get_" + prop.name.replace("-", "_").lower()
    
    def _interface_impl_funcname(self, cls, intf, method_name):
        
        method_prefix = intf.cfunc_prefix or intf.name.lower()
        module_predix = self._module_prefix_relative(intf.module, cls.module)
        if module_predix:
            method_prefix = module_predix + "_" + method_prefix
        
        return method_prefix + "_" + method_name
    
    def _is_property_init_required(self, obj):
        
        if obj.get_properties():
            return True
        
        for intf in obj.interfaces:
            if intf.properties:
                return True
        
        return False
    
    def _module_prefix(self, module):
        
        res = module.cfunc_prefix or module.name.lower()
        
        curmod = module
        while curmod.module:
            curmod = curmod.module
            tmp = curmod.cfunc_prefix or curmod.name.lower()
            if tmp:
                res = tmp + "_" + res
        
        return res
    
    def _module_prefix_relative(self, module, root):
        
        res = ""
        
        abspath_module = self._get_abs_module_path(module)
        abspath_root = self._get_abs_module_path(root)
        len_rootpath = len(abspath_root)

        relpath = []
        
        for idx, m in enumerate(abspath_module):
            if not relpath and idx < len_rootpath and m == abspath_root[idx]:
                continue
            relpath.append(m)
            
        for m in relpath:
            if res:
                res += "_"
            res += m.cfunc_prefix or m.name.lower()
                
        return res
            
    def _get_abs_module_path(self, module):
        
        res = [module]
        curmod = module
        while curmod.module:
            curmod = curmod.module
            res.insert(0, curmod)
                        
        return res
        