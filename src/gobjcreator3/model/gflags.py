from gobjcreator3.model.module import ModuleElement

class GFlags(ModuleElement):
    
    def __init__(self, name, codes):
        
        ModuleElement.__init__(self, name)
        
        self.codes = codes
