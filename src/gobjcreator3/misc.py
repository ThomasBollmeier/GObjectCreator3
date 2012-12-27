class PropGTypeInfo(object):
    
    def __init__(self):
        
        self.gtype_id = ""
        self.full_type_name = None
         
class PropValue(object):
    
    def __init__(self):
        
        self.literal = None
        self.number_info = None
        self.code_info = None
        self.boolean = None
        
class PropNumberInfo(object):
    
    def __init__(self, digits, decimals):
        
        self.digits = digits
        self.decimals = decimals
        
class PropCodeInfo(object):
    
    def __init__(self, enumeration_name, code_name):
        
        self.enumeration_name = enumeration_name
        self.code_name = code_name