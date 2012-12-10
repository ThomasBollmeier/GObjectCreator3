from gobjcreator3.model.clsintf import ClsIntf
from gobjcreator3.model.type import Type
from gobjcreator3.model.visibility import Visibility

class GObject(ClsIntf):
    
    def __init__(self, name):
        
        ClsIntf.__init__(self, name, Type.OBJECT)
        
        self.super_class = None
        self.constructor = None
        self.interfaces = []
        
        self.overridden = []
        
        self._attributes = []
        self._attributes_d = {}
        
        self._properties = []
        self._properties_d = {}
        
        self._signals = []
        self._signals_d = {}
        
    def add_constructor(self, method):
        
        self.constructor = method
        
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
                meth = cls._methods_d[method_name]
                if cls == self or meth.visibility != Visibility.PRIVATE:
                    return MethodInfo(meth, cls)
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
        
    def add_attribute(self, attr):

        cls = self
        while cls:
            if attr.name in cls._attributes_d:
                existing = cls._attributes_d[attr.name]
                if cls == self or existing.visibility != Visibility.PRIVATE:
                    raise Exception("Attribute '%s' has already been defined in '%s'!" % (attr.name, cls))
            cls = cls.super_class
            
        self._attributes_d[attr.name] = attr
        self._attributes.append(attr)
        
    def get_attribute(self, name):

        cls = self
        while cls:
            if name in cls._attributes_d:
                attr = cls._attributes_d[name]
                if cls == self or attr.visibility != Visibility.PRIVATE:
                    return attr
            cls = cls.super_class
            
        return None
    
    def get_attributes(self, include_inherited=False):
        
        res = self._attributes
        
        if not include_inherited:
            return res
        
        cls = self.super_class
        while cls:
            res = [a for a in cls._attributes if a.visibility != Visibility.PRIVATE] + res
            cls = cls.super_class
            
        return res

    def add_property(self, prop):

        cls = self
        while cls:
            if prop.name in cls._properties_d:
                raise Exception("Property '%s' has already been defined in '%s'!" % (prop.name, cls))
            cls = cls.super_class
            
        self._properties_d[prop.name] = prop
        self._properties.append(prop)
        
    def get_properties(self, include_inherited=False):
        
        res = self._properties
        
        if not include_inherited:
            return res
        
        cls = self.super_class
        while cls:
            res = cls._properties + res
            cls = cls.super_class
            
        return res
    
    def add_signal(self, signal):
        
        cls = self
        while cls:
            if signal.name in cls._signals_d:
                raise Exception("Signal '%s' has already been defined in '%s'!" % (signal.name, cls))
            cls = cls.super_class
        
        self._signals_d[signal.name] = signal    
        self._signals.append(signal)

    def get_signals(self, include_inherited=False):
        
        res = self._signals
        
        if not include_inherited:
            return res
        
        cls = self.super_class
        while cls:
            res = cls._signals + res
            cls = cls.super_class
            
        return res
            
class MethodInfo(object):
    
    def __init__(self, method, def_origin):
        
        self.method = method
        self.def_origin = def_origin
