from gobjcreator3.model.type import Type

class GError(Type):
    
    def __init__(self, name, error_codes):
        
        Type.__init__(self, name, Type.ERROR_DOMAIN)
        
        self.error_codes = error_codes
