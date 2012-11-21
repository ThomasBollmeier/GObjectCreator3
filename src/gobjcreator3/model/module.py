class ModuleElement(object):
    
    MODULE_SEP = '::'
    
    def __init__(self, name):
        
        self.name = name
        self.module = None
        
    def get_full_name(self):
        
        res = self.name
        
        module = self.module
        while module and module.name:
            res = module.name + ModuleElement.MODULE_SEP + res
            module = module.parent
            
        return res

class Module(ModuleElement):
    
    def __init__(self, name):
        
        ModuleElement.__init__(self, name)
        
        self.name = name
        
        self.modules = []
        self.types = []
        self.objects = []
        self.interfaces = []
        self.error_domains = []
        self.enumerations = []
        self.flags = []
        
    def get_path(self):
        
        path = []
        
        module = self
        
        while module:
            if module.name:
                path.insert(0, module.name)
            module = module.parent
            
        return path
            
    def add_module(self, module):
        
        self.modules.append(module)
        module.module = self
        
    def add_type(self, type_):
        
        self.types.append(type_)
        type_.module = self
        
    def add_object(self, obj):
        
        self.objects.append(obj)
        obj.module = self
        
    def add_interface(self, intf):
        
        self.interfaces.append(intf)
        intf.module = self
        
    def add_error_domain(self, error_domain):
        
        self.error_domains.append(error_domain)
        error_domain.module = self
        
    def add_enumeration(self, enum):
        
        self.enumerations.append(enum)
        enum.module = self
        
    def add_flag(self, flag):
        
        self.flags.append(flag)
        flag.module = self
        
TOPLEVEL = Module('') 