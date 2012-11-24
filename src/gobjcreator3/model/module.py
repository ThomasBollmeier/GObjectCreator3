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
    
    def __init__(self, name):
        
        ModuleElement.__init__(self, name)
        
        self.modules = []
        self._modules_d = {}
        
        self.types = []
        self._types_d = {}
        
        self.objects = []
        self._objects_d = {}
        
        self.interfaces = []
        self._interfaces_d = {}
        
        self.error_domains = []
        self._error_domains_d = {}
        
        self.enumerations = []
        self._enumerations_d = {}
        
        self.flags = []
        self._flags_d = {}

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
            
        for flag in module.flags:
            self.add_flag(flag)
                    
    def get_path(self):
        
        path = []
        
        module = self
        
        while module:
            if module.name:
                path.insert(0, module.name)
            module = module.parent
            
        return path
            
    def get_module(self, module_path):
        
        if not module_path:
            return self
                
        module_names = module_path.split(ModuleElement.MODULE_SEP)
        parent = self
        for module_name in module_names:
            if module_name in parent._modules_d:
                module = parent._modules_d[module_name]
            else:
                module = Module(module_name)
                parent.add_module(module)
            parent = module
            
        return module

    def add_module(self, module):
        
        if module.name in self._modules_d:
            existing_module = self._modules_d[module.name]
            existing_module.merge(module)
            return
        
        self.modules.append(module)
        self._modules_d[module.name] = module
        
        module.module = self
        
    def add_type(self, type_):
        
        if type_.name in self._types_d:
            raise Exception("Type '%s' has already been defined!" % type_.name)
        
        self.types.append(type_)
        self._types_d[type_.name] = type_
         
        type_.module = self
        
    def add_object(self, obj):

        if obj.name in self._objects_d:
            raise Exception("Object '%s' has already been defined!" % obj.name)
        
        self.objects.append(obj)
        self._objects_d[obj.name] = obj
        
        obj.module = self
        
    def add_interface(self, intf):

        if intf.name in self._interfaces_d:
            raise Exception("Interface '%s' has already been defined!" % intf.name)
        
        self.interfaces.append(intf)
        self._interfaces_d[intf.name] = intf
        
        intf.module = self
        
    def add_error_domain(self, error_domain):
        
        if error_domain.name in self._error_domains_d:
            raise Exception("Error domain '%s' has already been defined!" % error_domain.name)
        
        self.error_domains.append(error_domain)
        self._error_domains_d[error_domain.name] = error_domain
        
        error_domain.module = self
        
    def add_enumeration(self, enum):
        
        if enum.name in self._enumerations_d:
            raise Exception("Enumeration '%s' has already been defined!" % enum.name)
        
        self.enumerations.append(enum)
        self._enumerations_d[enum.name] = enum
        
        enum.module = self
        
    def add_flag(self, flag):
        
        if flag.name in self._flags_d:
            raise Exception("Flag '%s' has already been defined!" % flag.name)
        
        self.flags.append(flag)
        self._flags_d[flag.name] = flag
        
        flag.module = self
        
class RootModule(Module):

    def __init__(self):
        
        Module.__init__(self, '')

