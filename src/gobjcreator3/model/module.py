class ModuleElement(object):
    
    MODULE_SEP = '/'

    def __init__(self, name):
        
        self.name = name
        self.module = None
        self.filepath_origin = ""
        
    def get_fullname(self):
        
        res = self.name
        
        module = self.module
        while module and module.name:
            res = module.name + ModuleElement.MODULE_SEP + res
            module = module.module
            
        return res

class Module(ModuleElement):
    
    PARENT = ".."
    
    def __init__(self, name):
        
        ModuleElement.__init__(self, name)
        
        self._elements = []
        self._elements_d = {}

    def merge(self, module):
        
        for elem in module._elements:
            if not isinstance(elem, Module):
                self.add_element(elem)
            else:
                try:
                    existing_element = self._elements_d[elem.name]
                    if isinstance(existing_element, Module):
                        existing_element.merge(elem)
                    else:
                        raise Exception("'%s' has been already defined" % elem.name)
                except KeyError:
                    self.add_element(elem)
            
    def get_root(self):
        
        res = self
        while res.module:
            res = res.module
            
        return res
                    
    def get_path(self):
        
        path = []
        
        module = self
        
        while module:
            if module.name:
                path.insert(0, module.name)
            module = module.parent
            
        return path
            
    def get_module(self, path):
        
        res = self._get_element(path)
        if res and isinstance(res, Module):
            return res
        else:
            return None
        
    def get_type(self, path):
        
        res = self._get_element(path)
        if res and isinstance(res, Type) and res.category == Type.OTHER:
            return res
        else:
            return None

    def get_object(self, path):
        
        res = self._get_element(path)
        if res and isinstance(res, Type) and res.category == Type.OBJECT:
            return res
        else:
            return None
    
    def get_interface(self, path):
        
        res = self._get_element(path)
        if res and isinstance(res, Type) and res.category == Type.INTERFACE:
            return res
        else:
            return None
        
    def get_error_domain(self, path):
        
        res = self._get_element(path)
        if res and isinstance(res, Type) and res.category == Type.ERROR_DOMAIN:
            return res
        else:
            return None
    
    def get_enumeration(self, path):
        
        res = self._get_element(path)
        if res and isinstance(res, Type) and res.category == Type.ENUMERATION:
            return res
        else:
            return None
        
    def get_flags(self, path):
        
        res = self._get_element(path)
        if res and isinstance(res, Type) and res.category == Type.FLAGS:
            return res
        else:
            return None
        
    def get_type_element(self, path):
        
        res = self._get_element(path)
        if res and isinstance(res, Type):
            return res
        else:
            return None
        
    def get_element(self, path):
        
        return self._get_element(path)
        
    def _get_element(self, path):
        
        if not path:
            return self
        
        names = path.split(ModuleElement.MODULE_SEP)
        if names[0]:
            parent_module = self 
        else: # absolute path:
            parent_module = self.get_root()
            names = names[1:]
            
        if len(names) == 1:
            element_name = names[0]
            module_names = []
        else:
            element_name = names[-1]
            module_names = names[:-1]
            
        for module_name in module_names:
            if module_name != Module.PARENT:
                parent_module = parent_module._get_element(module_name)
            else:
                parent_module = parent_module.module
            if not isinstance(parent_module, Module):
                raise Exception("'%s' is not a module!" % module_name)
            
        try:
            return parent_module._elements_d[element_name]      
        except KeyError:
            return None

    def _get_type_elements(self, category):
        
        return [elem for elem in self._elements if isinstance(elem, Type) and elem.category == category]
    
    def _get_modules(self):

        return [elem for elem in self._elements if isinstance(elem, Module)]
    
    modules = property(_get_modules)

    def _get_types(self):
        
        return self._get_type_elements(Type.OTHER)
    
    types = property(_get_types)
         
    def _get_objects(self):
        
        return self._get_type_elements(Type.OBJECT)
    
    objects = property(_get_objects)
         
    def _get_interfaces(self):
        
        return self._get_type_elements(Type.INTERFACE)
    
    interfaces = property(_get_interfaces)
         
    def _get_error_domains(self):
        
        return self._get_type_elements(Type.ERROR_DOMAIN)
            
    error_domains = property(_get_error_domains)
    
    def _get_enumerations(self):
        
        return self._get_type_elements(Type.ENUMERATION)
    
    enumerations = property(_get_enumerations)
    
    def _get_flags(self):
        
        return self._get_type_elements(Type.FLAGS)
    
    flags = property(_get_flags)
            
    def add_element(self, element):
        
        if element.name in self._elements_d:
            raise Exception("'%s' has been already defined" % element.name)
            
        self._elements_d[element.name] = element
        self._elements.append(element)
        
        element.module = self
                
class RootModule(Module):

    def __init__(self):
        
        Module.__init__(self, '')

from gobjcreator3.model.type import Type