from gobjcreator3.model.module import ModuleElement

class ClsIntf(ModuleElement):
    
    def __init__(self, name):
        
        ModuleElement.__init__(self, name)
        
        self._methods = []
        self._methods_d = {}
        
    def _get_methods(self):
        
        return self._methods
    
    methods = property(_get_methods)
        
    def add_method(self, method):
        
        if method.name in self._methods_d:
            raise Exception("Method '%s' has been defined already!" % method.name)
        
        self._methods.append(method)
        self._methods_d[method.name] = method
        
        
        
        