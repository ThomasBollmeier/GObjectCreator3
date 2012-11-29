from gobjcreator3.model.clsintf import ClsIntf
from gobjcreator3.model.type import Type

class GObject(ClsIntf):
    
    def __init__(self, name):
        
        ClsIntf.__init__(self, name, Type.OBJECT)
        
        self.super_class = None
        self.interfaces = []
        
        self.attributes = []
        self.properties = []
        self.signals = []
