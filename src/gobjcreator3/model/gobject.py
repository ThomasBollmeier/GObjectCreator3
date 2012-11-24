from gobjcreator3.model.module import ModuleElement

class GObject(ModuleElement):
    
    def __init__(self, name):
        
        ModuleElement.__init__(self, name)
        
        self.super_class = None
        self.interfaces = []
        
        self.methods = []
        self.attributes = []
        self.properties = []
        self.signals = []
