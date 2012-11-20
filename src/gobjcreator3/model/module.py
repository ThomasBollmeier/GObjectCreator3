class Module(object):
    
    def __init__(self, name):
        
        self.name = name
        
        self.modules = []
        self.types = []
        self.objects = []
        self.interfaces = []
        self.error_domains = []
        self.enums = []
        self.flags = []
        
    def add_module(self, module):
        
        self.modules.append(module)
        
TOPLEVEL = Module('') 