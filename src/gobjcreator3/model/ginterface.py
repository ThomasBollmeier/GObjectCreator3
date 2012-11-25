from gobjcreator3.model.module import ModuleElement

class GInterface(ModuleElement):
    
    def __init__(self, name):
        
        ModuleElement.__init__(self, name)
        
        self.methods = []
