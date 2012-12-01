from gobjcreator3.model.clsintf import ClsIntf
from gobjcreator3.model.type import Type

class GObject(ClsIntf):
    
    def __init__(self, name):
        
        ClsIntf.__init__(self, name, Type.OBJECT)
        
        self.super_class = None
        self.interfaces = []
        
        self.overridden = []
        self.attributes = []
        self.properties = []
        self.signals = []
        
    def add_method(self, method):
        
        if self.get_method(method.name):
            raise Exception("Method '%s' has already been defined" % method.name)
        
        ClsIntf.add_method(self, method)
        
    def get_method(self, method_name):
        
        info = self.get_method_info(method_name)
        
        return info and info.method or None
        
    def get_method_info(self, method_name):
        
        cls = self
        while cls:
            if method_name in cls._methods_d:
                return MethodInfo(cls._methods_d[method_name], cls)
            for intf in cls.interfaces:
                if method_name in intf._methods_d:
                    return MethodInfo(intf._methods_d[method_name], intf)
            cls = cls.super_class
            
        return None
    
    def override(self, method_name):
        
        info = self.get_method_info(method_name)
        if not info:
            raise Exception("Method '%s' has not been defined!" % method_name)
        
        if info.method.is_final:
            raise Exception("Final method '%s' cannot be overridden!" % method_name)
        
        self.overridden.append(info.method)

class MethodInfo(object):
    
    def __init__(self, method, def_origin):
        
        self.method = method
        self.def_origin = def_origin
        