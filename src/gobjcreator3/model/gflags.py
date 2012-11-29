from gobjcreator3.model.type import Type

class GFlags(Type):
    
    def __init__(self, name, codes):
        
        Type.__init__(self, name, Type.FLAGS)
        
        self.codes = codes
