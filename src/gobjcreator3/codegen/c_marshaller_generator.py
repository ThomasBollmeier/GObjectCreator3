import faberscriptorum
import os
import gobjcreator3.model.type as type_def
from gobjcreator3.codegen.name_creator import NameCreator

class CMarshallerNameCreator(object):
    
    def __init__(self, func_prefix):
        
        self._name_creator = NameCreator()
        
        self._func_prefix = func_prefix
        
        self._builtin_name_map = {"string": "STRING",
                                  "boolean": "BOOLEAN",
                                  "integer": "INT",
                                  "unsigned integer": "UINT",
                                  "float": "FLOAT",
                                  "double": "DOUBLE",
                                  "any": "POINTER"
                                  }
        
        self._builtin_type_map = {"string": "gpointer",
                                  "boolean": "gboolean",
                                  "integer": "gint",
                                  "unsigned integer": "guint",
                                  "float": "gfloat",
                                  "double": "double",
                                  "any": "gpointer"
                                  }
        
        self._builtin_func_map = {"string": "g_marshal_value_peek_string",
                                  "boolean": "g_value_get_boolean",
                                  "integer": "g_value_get_int",
                                  "unsigned integer": "g_value_get_uint",
                                  "float": "g_value_get_float",
                                  "double": "g_value_get_double",
                                  "any": "g_value_get_pointer"
                                  }
                
    def create_marshaller_name(self, signal):
        
        res = self._func_prefix + "_marshal_"
        res += self._create_signature_part(signal)
        
        return res
    
    def create_marshaller_type_name(self, signal):
    
        return "GMarshalFunc_" + self._create_signature_part(signal)
    
    def get_param_type_name(self, type_):
        
        if not isinstance(type_, type_def.Type):
            raise Exception('References or lists are not supported as signal parameters')
        
        catg = type_.category
        if catg == type_def.Type.BUILTIN:
            res = self._builtin_type_map[type_.name]
        else:
            res = self._name_creator.create_full_type_name(type_, with_asterisk=True)
        
        return res        
 
    def get_peek_func_name(self, type_):
        
        if not isinstance(type_, type_def.Type):
            raise Exception('References or lists are not supported as signal parameters')
        
        catg = type_.category
        if catg == type_def.Type.BUILTIN:
            res = self._builtin_func_map[type_.name]
        elif catg == type_def.Type.ENUMERATION:
            res = "g_value_get_int"
        elif catg == type_def.Type.OBJECT or catg == type_def.Type.INTERFACE:
            res = "g_value_get_object"
        else:
            raise Exception('Unsupported type category for signal parameters')
        
        return res        
    
    def _create_signature_part(self, signal):
 
        res = "VOID__" #TODO: Add support for signals with result parameters
        
        if signal.parameters:
            first = True
            for param in signal.parameters:
                if not first:
                    res += "_"
                else:
                    first = False
                res += self._get_type_name(param)
        else:
            res += "VOID"
        
        return res
    
    def _get_type_name(self, param):
        
        if not isinstance(param.type, type_def.Type):
            raise Exception('References or lists are not supported as signal parameters')
        
        catg = param.type.category
        if catg == type_def.Type.BUILTIN:
            res = self._builtin_name_map[param.type.name]
        elif catg == type_def.Type.ENUMERATION:
            res = "ENUM"
        elif catg == type_def.Type.OBJECT:
            res = "OBJECT"
        elif catg == type_def.Type.INTERFACE:
            res = "IFACE"
        else:
            raise Exception('Unsupported type category for signal parameters')
        
        return res

class CMarshallerGenerator(object):
    """
    Helper class to generate marshaller functions
    """
    
    def __init__(self, 
                 header_guard,
                 func_prefix,
                 signals, 
                 output
                 ):
        
        self._header_guard = header_guard
        self._name_creator = CMarshallerNameCreator(func_prefix)
        self._signals = signals
        self._gen_out = output
        
        self._codegenerator = self._create_codegenerator()
        
        self._template_dir = os.path.dirname(__file__) + os.sep + "templates" + os.sep + "c"
        self._template_dir = os.path.abspath(self._template_dir)

    def generate_header(self, path_to_gen_file):
        
        self._gen_from_template("marshaller_header.template", path_to_gen_file)
        
    def generate_source(self, path_to_gen_file):
        
        self._gen_from_template("marshaller_source.template", path_to_gen_file)
    
    def _create_codegenerator(self):
 
        res = faberscriptorum.API()
        res.setEditableSectionStyle(res.Language.C)
        
        res["length"] = len
        res["HEADER_GUARD"] = self._header_guard
        
        marshallers = self._get_marshallers(self._signals)
        res["marshallers"] = marshallers
        res["marshaller_names"] = list(marshallers.keys())
        res["param_type"] = self._name_creator.get_param_type_name
        
        return res
    
    def _gen_from_template(self, template_file, path_to_gen_file):
        
        self._gen_out.prepare_file_creation(path_to_gen_file, self._codegenerator)
        
        template_path = self._template_dir + os.sep + template_file
        
        buffer = self._codegenerator.createStringOut()
        self._codegenerator.createCode(template_path, buffer)
        
        lines = buffer.content.split(os.linesep)
        lines = self._remove_adjacent_empty_lines(lines)
        
        self._gen_out.visit_text_file(path_to_gen_file, lines)
        
    def _remove_adjacent_empty_lines(self, lines): 
        
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
    
    def _get_marshallers(self, signals):
        
        res = {} 
        for signal in signals:
            name = self._name_creator.create_marshaller_name(signal)
            if not name in res:
                typedef_name = self._name_creator.create_marshaller_type_name(signal)
                res[name] = MarshallerInfo(
                                           self._name_creator,
                                           name, 
                                           typedef_name, 
                                           signal.parameters
                                           )
        
        return res
    
class MarshallerInfo(object):
    
    def __init__(self, 
                 name_creator,
                 method_name, 
                 typedef_name,
                 parameters,
                 ):
        
        self.method_name = method_name
        self.typedef_name = typedef_name
        self._parameters = []
        for idx, param in enumerate(parameters):
            name = "arg%d" % (idx + 1)
            type_ = name_creator.get_param_type_name(param.type)
            peek_func = name_creator.get_peek_func_name(param.type)
            offset = idx + 1
            self._parameters.append(MarshallerParam(name, 
                                                    type_, 
                                                    peek_func, 
                                                    offset))
            
    def get_num_arguments(self):
        
        return len(self._parameters) + 1
        
    def get_parameters(self):
        
        return self._parameters
    
class MarshallerParam(object):
    
    def __init__(self,
                 name,
                 type_,
                 peek_func,
                 offset
                 ):
        
        self.name = name
        self.type = type_
        self.peek_func = peek_func
        self.offset = offset
