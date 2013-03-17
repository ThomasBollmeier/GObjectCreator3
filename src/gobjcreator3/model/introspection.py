
class MethodIntroData(object):
    
    def __init__(self, method_name, skip=False):
        
        self.method_name = method_name
        self.skip = skip

class ParamIntroData(object):
    
    def __init__(self, param_name):
        
        self.param_name = param_name 