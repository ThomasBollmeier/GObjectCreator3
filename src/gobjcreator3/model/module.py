class ModuleElement(object):
    
    MODULE_SEP = '::'
    
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
    
    ELEM_MODULE = 1
    ELEM_TYPE = 2
    ELEM_OBJECT = 3
    ELEM_INTERFACE = 4
    ELEM_ERROR_DOMAIN = 5
    ELEM_ENUMERATION = 6
    ELEM_FLAGS = 7
    
    _elem_catg_names = ['module', 
                        'type', 
                        'object',
                        'interface',
                        'error domain',
                        'enumeration',
                        'flags' 
                        ]
    
    def __init__(self, name):
        
        ModuleElement.__init__(self, name)
        
        self._elements = []
        self._elements_d = {}

    def merge(self, module):
        
        for m in module.modules:
            self.add_module(m)
        
        for type_ in module.types:
            self.add_type(type_)
            
        for obj in module.objects:
            self.add_object(obj)
            
        for intf in module.interfaces:
            self.add_interface(intf)
            
        for error_domain in module.error_domains:
            self.add_error_domain(error_domain)
            
        for enum in module.enumerations:
            self.add_enumeration(enum)
            
        for flags in module.flags:
            self.add_flags(flags)
            
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
        
        return self._get_element(path, Module.ELEM_MODULE)
    
    def get_type(self, path):
        
        return self._get_element(path, Module.ELEM_TYPE)

    def get_object(self, path):
        
        return self._get_element(path, Module.ELEM_OBJECT)
    
    def get_interface(self, path):
        
        return self._get_element(path, Module.ELEM_INTERFACE)
    
    def get_error_domain(self, path):
        
        return self._get_element(path, Module.ELEM_ERROR_DOMAIN)
    
    def get_enumeration(self, path):
        
        return self._get_element(path, Module.ELEM_ENUMERATION)
    
    def get_flags(self, path):
        
        return self._get_element(path, Module.ELEM_FLAGS)

    def add_module(self, module):
        
        existing_module = self._get_element(module.name, Module.ELEM_MODULE)
        if existing_module:
            existing_module.merge(module)
            return
        
        self._add_element(module, Module.ELEM_MODULE, check_for_duplicates=False)
        module.module = self
        
    def add_type(self, type_):
        
        self._add_element(type_, Module.ELEM_TYPE) 
        type_.module = self
        
    def add_object(self, obj):

        self._add_element(obj, Module.ELEM_OBJECT) 
        obj.module = self
        
    def add_interface(self, intf):
        
        self._add_element(intf, Module.ELEM_INTERFACE) 
        intf.module = self
        
    def add_error_domain(self, error_domain):

        self._add_element(error_domain, Module.ELEM_ERROR_DOMAIN) 
        error_domain.module = self
        
    def add_enumeration(self, enum):
        
        self._add_element(enum, Module.ELEM_ENUMERATION) 
        enum.module = self
        
    def add_flags(self, flags):

        self._add_element(flags, Module.ELEM_FLAGS) 
        flags.module = self
        
    def _get_element(self, path, required_catg):
        
        if not path:
            if required_catg == Module.ELEM_MODULE:
                return self
            else:
                raise Exception('No path was passed!')
        
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
            parent_module = parent_module._get_element(module_name, Module.ELEM_MODULE)
        
        if element_name not in parent_module._elements_d:
            return None
        else:
            catg, element = parent_module._elements_d[element_name]
            if catg == required_catg:
                return element
            else:
                raise Exception("'%s' is no %s" % \
                                (element_name, Module._elem_catg_names[required_catg-1]))
            
    def _get_elements(self, catg):
        
        return [elem[1] for elem in self._elements if elem[0] == catg]
    
    def _get_modules(self):
        return self._get_elements(Module.ELEM_MODULE)
    
    modules = property(_get_modules)

    def _get_types(self):
        return self._get_elements(Module.ELEM_TYPE)
    
    types = property(_get_types)
         
    def _get_objects(self):
        return self._get_elements(Module.ELEM_OBJECT)
    
    objects = property(_get_objects)
         
    def _get_interfaces(self):
        return self._get_elements(Module.ELEM_INTERFACE)
    
    interfaces = property(_get_interfaces)
         
    def _get_error_domains(self):
        return self._get_elements(Module.ELEM_ERROR_DOMAIN)
    
    error_domains = property(_get_error_domains)
    
    def _get_enumerations(self):
        return self._get_elements(Module.ELEM_ENUMERATION)
    
    enumerations = property(_get_enumerations)
    
    def _get_flags(self):
        return self._get_elements(Module.ELEM_FLAGS)
    
    flags = property(_get_flags)
            
    def _add_element(self, element, catg, check_for_duplicates=True):
        
        if check_for_duplicates:
            if self._get_element(element.name, catg) != None:
                raise Exception("'%s' has been already defined" % element.name)
            
        self._elements_d[element.name] = (catg, element)
        self._elements.append((catg, element))
                
class RootModule(Module):

    def __init__(self):
        
        Module.__init__(self, '')

