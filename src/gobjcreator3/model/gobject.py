from gobjcreator3.model.clsintf import ClsIntf

class GObject(ClsIntf):
    
    def __init__(self, name):
        
        ClsIntf.__init__(self, name)
        
        self.super_class = None
        self.interfaces = []
        
        self.attributes = []
        self.properties = []
        self.signals = []
