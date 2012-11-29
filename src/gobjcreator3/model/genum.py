from gobjcreator3.model.type import Type

class GEnum(Type):
    
    def __init__(self, name, code_names_values):
        
        Type.__init__(self, name, Type.ENUMERATION)
        
        self.code_names_values = code_names_values
