class Attribute(object):
    
    def __init__(self, 
                 name,
                 type_,
                 visibility,
                 is_static
                 ):
        
        self.name = name
        self.type = type_
        self.visibility = visibility
        self.is_static = is_static