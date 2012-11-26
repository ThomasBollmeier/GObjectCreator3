from gobjcreator3.model.module import ModuleElement

class GEnum(ModuleElement):
    
    def __init__(self, name, code_names_values):
        
        ModuleElement.__init__(self, name)
        
        self.code_names_values = code_names_values
