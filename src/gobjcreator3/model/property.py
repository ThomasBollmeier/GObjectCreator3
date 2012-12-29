class Property(object):

    def __init__(self,
        name,
        type_,
        access,
        description,
        gtype,
        min_,
        max_,
        default
        ):

        self.name = name
        self.type = type_
        self.access = access
        self.description = description
        self.gtype = gtype
        self.min = min_
        self.max = max_
        self.default = default
        
    def is_readable(self):
        
        return PropAccess.READ in self.access

    def is_writable(self):
        
        return PropAccess.WRITE in self.access

class PropType:

    BOOLEAN = 1
    BYTE = 2
    INTEGER = 3
    FLOAT = 4
    DOUBLE = 5
    STRING = 6
    POINTER = 7
    OBJECT = 8
    ENUMERATION = 9

class PropAccess:

    READ = 1
    WRITE = 2
    INIT = 3
    INIT_ONLY = 4

class PropGTypeValue(object):

    def __init__(self, gtype_id, type_):

        self.gtype_id = gtype_id
        self.type = type_
        
    def __str__(self):
        
        if self.gtype_id:
            return self.gtype_id
        elif self.type:
            return "gtypeof(%s)" % self.type
        else:
            return ""
        
class PropValue(object):
    
    def __init__(self):
        
        self.literal = None
        self.number_info = None
        self.code_info = None
        self.boolean = None
        
    def __str__(self):
        
        if self.literal:
            return self.literal
        elif self.number_info:
            if not self.number_info.decimals:
                return str(self.number_info.digits)
            else:
                return "%d.%d" % (self.number_info.digits, self.number_info.decimals)
        elif self.code_info:
            return "%s->%s" % (self.code_info.enumeration, self.code_info.code_name)
        elif self.boolean is not None:
            return self.boolean and "true" or "false"
        else:
            return "<undefined property value>"
        
class PropNumberInfo(object):
    
    def __init__(self, digits, decimals):
        
        self.digits = digits
        self.decimals = decimals
        
class PropCodeInfo(object):
    
    def __init__(self, enumeration, code_name):
        
        self.enumeration = enumeration
        self.code_name = code_name        
