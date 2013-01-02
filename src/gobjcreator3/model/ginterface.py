from gobjcreator3.model.clsintf import ClsIntf
from gobjcreator3.model.type import Type

class GInterface(ClsIntf):
    
    def __init__(self, name):
        
        ClsIntf.__init__(self, name, Type.INTERFACE)
        
        self._methods = []
        self._methods_d = {}
        
    def add_method(self, method):
        
        if method.name in self._methods_d:
            raise Exception("Method '%s' has already been defined in interface '%s'" % (method.name, self.name))
        
        self._methods.append(method)
        self._methods_d[method.name] = method
        
    def get_methods(self):
        
        return self._methods
    
    methods = property(get_methods)
