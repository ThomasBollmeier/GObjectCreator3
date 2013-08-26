
class MethodIntroData(object):
    
    def __init__(self):
        
        self.skip = False

class ParamIntroData(object):
    
    def __init__(self):
        
        self.transfer = None
        self.out_alloc = None
        self.allow_none = None
        self.callback = None
        self.user_data = None
        self.array = None
        self.array_element = None

class ArrayElementIntroData(object):
    
    def __init__(self):
        
        self.type = None
        self.key_type = None
        self.value_type = None