from gobjcreator3.model.module import ModuleElement

class GError(ModuleElement):
    
    def __init__(self, name, error_codes):
        
        ModuleElement.__init__(self, name)
        
        self.error_codes = error_codes
