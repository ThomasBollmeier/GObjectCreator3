from gobjcreator3.model.clsintf import ClsIntf
from gobjcreator3.model.type import Type

class GInterface(ClsIntf):
    
    def __init__(self, name):
        
        ClsIntf.__init__(self, name, Type.INTERFACE)
        
        self._methods = []
        self._methods_d = {}
        
        self._properties = []
        self._properties_d = {}
        
        self._signals = []
        self._signals_d = {}
        
    def add_method(self, method):
        
        if method.name in self._methods_d:
            raise Exception("Method '%s' has already been defined in interface '%s'" % (method.name, self.name))
        
        self._methods.append(method)
        self._methods_d[method.name] = method
        
    def get_methods(self):
        
        return self._methods
    
    methods = property(get_methods)
    
    def add_property(self, prop):
        
        if prop.name in self._properties_d:
            raise Exception("Property '%s' has already been defined in interface '%s'" % (prop.name, self.name))
        
        self._properties.append(prop)
        self._properties_d[prop.name] = prop
        
    def get_properties(self):
        
        return self._properties
    
    properties = property(get_properties)
    
    def add_signal(self, signal):
        
        if signal.name in self._signals_d:
            raise Exception("Signal '%s' has already been defined in interface '%s'" % (signal.name, self.name))
        
        self._signals.append(signal)
        self._signals_d[signal.name] = signal
        
    def get_signals(self):
        
        return self._signals
    
    signals = property(get_signals)
