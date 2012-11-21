class Type(object):
    
    MODULE_SEP = '::'
    
    def __init__(self, name):
        
        self.name = name
        self.module = None
        
    def get_full_name(self):
        
        res = self.name
        
        module = self.module
        while module and module.name:
            res = module.name + Type.MODULE_SEP + res
            module = module.parent
            
        return res
