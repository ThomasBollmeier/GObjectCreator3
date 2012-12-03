class Property(object):

    def __init__(self,
        name,
        type_,
        access,
        description,
        gtype,
        min_,
        max_,
        default,
        auto_create
        ):

        self.name = name
        self.type = type_
        self.access = access
        self.description = description
        self.gtype = gtype
        self.min = min_
        self.max = max_
        self.default = default
        self.auto_create = auto_create

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

    READ_ONLY = 1
    INITIAL_WRITE = 2
    READ_WRITE = 3

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
    
    def __init__(self, name, is_codename):
        
        self.name = name
        self.is_codename = is_codename        