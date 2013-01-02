from gobjcreator3.model.type import Type

class ClsIntf(Type):
    
    def __init__(self, name, category):
        
        Type.__init__(self, name, category)
        
        self.cfunc_prefix = ""
        
        
        