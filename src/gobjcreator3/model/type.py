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
        
    def __str__(self):
        
        namespace = ""
        cur_module = self.module
        
        while cur_module:
            if namespace:
                namespace = "/" + namespace
            namespace = cur_module.name + namespace
            cur_module = cur_module.module
            
        res = self.name
            
        if namespace:
            res = namespace + "/" + res
            
        return res 
        
class BuiltIn(Type):
    
    def __init__(self, name):
        
        Type.__init__(self, name, Type.BUILTIN)
        
    def __str__(self):
        
        return self.name
        
class Reference(object):
    
    def __init__(self, type_):
        
        self.target_type = type_
        
    def __str__(self):
        
        return "%s*" % self.target_type
        
class List(object):
    
    def __init__(self, line_type):
        
        self.line_type = line_type
        
    def __str__(self):
        
        return "%s[]" % self.line_type
