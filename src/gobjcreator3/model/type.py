from gobjcreator3.model.module import ModuleElement

class Type(ModuleElement):
    
    OBJECT = 1
    INTERFACE = 2
    ENUMERATION = 3
    ERROR_DOMAIN = 4
    FLAGS = 5
    BUILTIN = 6
    OTHER = 7
        
    def __init__(self, name, category):
        
        ModuleElement.__init__(self, name)
        self.category = category
        
class BuiltIn(Type):
    
    def __init__(self, name):
        
        Type.__init__(self, name, Type.BUILTIN)
