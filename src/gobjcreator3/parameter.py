class ArgType(object):
    
    def __init__(self):
        pass
    
class BuiltIn(ArgType):
    
    def __init__(self, name):
        
        ArgType.__init__(self)
        self.name = name
        
    def __str__(self):
        
        return self.name

class FullTypeName(ArgType):
    
    def __init__(self, name, module_path=[], is_absolute_type = True):
        
        ArgType.__init__(self)
        self.name = name
        self.module_path = module_path
        self.is_absolute_type = is_absolute_type
        
    def __str__(self):
        
        res = self.name
        
        if self.module_path:
            res = "/".join(self.module_path) + "/" + res
            
        if self.is_absolute_type:
            res = "/" + res
        
        return res
        
class ListOf(ArgType):
    
    def __init__(self, element_type):
        
        ArgType.__init__(self)
        self.element_type = element_type
        
    def __str__(self):
        
        return "%s[]" % self.element_type
        
class RefTo(ArgType):
    
    def __init__(self, ref_type):
        
        ArgType.__init__(self)
        self.ref_type = ref_type
        
    def __str__(self):
        
        return "%s*" % self.ref_type
    
class Parameter(object):
    
    IN = 1
    OUT = 2
    IN_OUT = 3
    
    def __init__(self, name, arg_type, category=IN):
        
        self.name = name
        self.arg_type = arg_type
        self.category = category
        self.properties = {}
        
class ConstructorParam(Parameter):
    
    def __init__(self, name, arg_type, category, bind_to_property):
        
        Parameter.__init__(self, name, arg_type, category)
        
        self.bind_to_property = bind_to_property
        
class PropertyInit(object):
    
    def __init__(self, name, value):
        
        self.name = name
        self.value = value
        
        
        