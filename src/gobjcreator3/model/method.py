class Method(object):
    
    VISI_PUBLIC = 1
    VISI_PROTECTED = 2
    VISI_PRIVATE = 3
    
    def __init__(self, name):
        
        self.name = name
        self.visibility = Method.VISI_PRIVATE
        self.is_static = False
        self.is_abstract = False
        self.is_final = False
        
        self.parameters = []
        
    def set_static(self, is_static=True):
        
        if self.is_abstract and is_static:
            raise Exception("Abstract method '%s' cannot be set to static" % self.name)

        self.is_static = is_static
        
    def set_abstract(self, is_abstract=True):
        
        if self.is_static and is_abstract:
            raise Exception("Static method '%s' cannot be set to abstract" % self.name)

        if self.is_final and is_abstract:
            raise Exception("Final method '%s' cannot be set to abstract" % self.name)
        
        if self.visibility == Method.VISI_PRIVATE and is_abstract:
            raise Exception("Private method '%s' cannot be set to abstract" % self.name)
                    
        self.is_abstract = is_abstract
            
    def set_final(self, is_final=True):
        
        if self.is_abstract and is_final:
            raise Exception("Abstract method '%s' cannot be set to final" % self.name)
        
        self.is_final = is_final
        
class Parameter(object):
    
    IN = 1
    OUT = 2
    IN_OUT = 3
    
    def __init__(self, name, type_, direction=IN):
        
        self.name = name
        self.type = type_
        self.direction = direction
