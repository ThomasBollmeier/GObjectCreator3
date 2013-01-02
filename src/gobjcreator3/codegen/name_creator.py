from gobjcreator3.model.type import Type, BuiltIn, Reference, List

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
            res = "GList*" #self.create_full_type_name(type_.line_type) + "*"
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
        
        if isinstance(type_, BuiltIn):
            return {"string": "G_TYPE_STRING",
                    "boolean": "G_TYPE_BOOLEAN",
                    "integer": "G_TYPE_INT",
                    "unsigned integer": "G_TYPE_UINT",
                    "float": "G_TYPE_FLOAT",
                    "double": "G_TYPE_DOUBLE",
                    "any": "G_TYPE_POINTER"}[type_.name]
        
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
