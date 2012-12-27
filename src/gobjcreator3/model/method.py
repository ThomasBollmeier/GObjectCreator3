from gobjcreator3.model.visibility import Visibility 

class Method(object):
    
    def __init__(self, name):
        
        self.name = name
        self.visibility = Visibility.PRIVATE
        self.is_static = False
        self.is_abstract = False
        self.is_final = False
        
        self.parameters = []
        
    def set_static(self, is_static=True):
        
        if self.is_abstract and is_static:
            raise Exception("Abstract method '%s' cannot be set to static" % self.name)

        self.is_static = is_static

        if is_static:
            self.is_final = True 
        
    def set_abstract(self, is_abstract=True):
        
        if self.is_static and is_abstract:
            raise Exception("Static method '%s' cannot be set to abstract" % self.name)

        if self.is_final and is_abstract:
            raise Exception("Final method '%s' cannot be set to abstract" % self.name)
        
        if self.visibility == Visibility.PRIVATE and is_abstract:
            raise Exception("Private method '%s' cannot be set to abstract" % self.name)
                    
        self.is_abstract = is_abstract
                    
    def set_final(self, is_final=True):
        
        if self.is_abstract and is_final:
            raise Exception("Abstract method '%s' cannot be set to final" % self.name)
        
        self.is_final = is_final
        
class ConstructorMethod(Method):
    
    def __init__(self):
        
        Method.__init__(self, "")

        self.is_static = True
        self.is_abstract = False
        self.is_final = True
        
        self.prop_inits = []
        
    def set_static(self, is_static=True):
        
        raise Exception("'set_static' must not be called for constructors")
                
    def set_abstract(self, is_abstract=True):
        
        raise Exception("'set_abstract' must not be called for constructors")
                    
    def set_final(self, is_final=True):
        
        raise Exception("'set_final' must not be called for constructors")
                
class Parameter(object):
    
    IN = 1
    OUT = 2
    IN_OUT = 3
    
    def __init__(self, name, type_, direction=IN):
        
        self.name = name
        self.type = type_
        self.direction = direction
        self.modifiers = []
        
class ConstructorParam(Parameter):
    
    def __init__(self, name, type_, direction, bind_to_property):
        
        Parameter.__init__(self, name, type_, direction)
        
        self.bind_to_property = bind_to_property

class PropertyInit(object):
    
    def __init__(self, name, value):
        
        self.name = name
        self.value = value