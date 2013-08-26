
class ISpecMethod(object):
    
    def __init__(self):
        
        self.skip = False
        
class ISpecParam(object):
    
    def __init__(self):
        
        self.transfer = None
        self.out_alloc = None
        self.allow_none = None
        self.callback = None
        self.user_data = None
        self.array = None
        self.array_element = None
        
class Transfer(object):
    
    NONE = 1
    CONTAINER = 2
    FULL = 3
    
class OutAlloc(object):
    
    CALLER = 1
    CALLEE = 2
    
class Callback(object):
    
    def __init__(self):
        
        self.user_data_param = None
        self.scope = None
        
class Scope(object):
    
    CALL = 1
    ASYNC = 2
    NOTIFIED = 3
    
class Array(object):
    
    def __init__(self):
        
        self.fixed_size = None
        self.length_param = None
        self.zero_terminated = None
        
class ArrayElement(object):
    
    def __init__(self):
        
        self.type = None
        self.key_type = None
        self.value_type = None
