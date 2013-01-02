from gobjcreator3.model.type import Type
from gobjcreator3.model.clsintf import ClsIntf
from gobjcreator3.model.visibility import Visibility

class GObject(ClsIntf):
    
    def __init__(self, name):
        
        ClsIntf.__init__(self, name, Type.OBJECT)
        
        self.is_abstract = False
        self.is_final = False
        self.super_class = None
        self.constructor = None
        
        self._interfaces = []
        
        self._methods = []
        self._methods_d = {}
        
        self.overridden = []
        
        self._attributes = []
        self._attributes_d = {}
        
        self._properties = []
        self._properties_d = {}
        
        self._signals = []
        self._signals_d = {}
        
    def implement(self, intf):
        
        self._interfaces.append(intf)
        for method in intf.methods:
            self.add_method(method, intf)
        
    def get_interfaces(self):
        
        return self._interfaces
    
    interfaces = property(get_interfaces)
        
    def add_constructor(self, method):
        
        self.constructor = method
        
    def add_method(self, method, intf=None):
        
        info = self.get_method_info(method.name, intf)
        
        if info:
            raise Exception("Method '%s' has already been defined in class '%s'" % (method.name, info.def_origin))
        
        key = (method.name, intf)
                
        self._methods.append((method, intf))
        self._methods_d[key] = method
         
    def get_method_info(self, method_name, intf=None):
        
        method_key = (method_name, intf)
        cls = self
        while cls:
            if method_key in cls._methods_d:
                meth = cls._methods_d[method_key]
                if cls == self or meth.visibility != Visibility.PRIVATE:
                    return MethodInfo(cls, meth, intf)
            cls = cls.super_class

        return None
    
    def get_methods(self):
        
        return self._methods
    
    methods = property(get_methods)
    
    def override(self, method_name, intf, new_visibility):
        
        info = self.get_method_info(method_name, intf)
        if not info:
            raise Exception("Method '%s' has not been defined!" % method_name)
        
        if info.method.is_final:
            raise Exception("Final method '%s' cannot be overridden!" % method_name)
        
        if new_visibility != info.method.visibility:
            raise Exception("Override must not change visibility of method '%s'!" % method_name)
        
        self.overridden.append((method_name, intf))
        
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
    
    def has_protected_members(self):
        
        has_prot_attrs = bool([attr for attr in self._attributes if attr.visibility == Visibility.PROTECTED])
        if has_prot_attrs:
            return True
        else:
            return bool([meth for meth in self.methods if meth[0].visibility == Visibility.PROTECTED])
            
    def has_signals(self):
        
        return bool(self.get_signals())
        
class MethodInfo(object):
    
    def __init__(self, def_origin, method, interface):
        
        self.def_origin = def_origin
        self.method = method
        self.interface = interface
        