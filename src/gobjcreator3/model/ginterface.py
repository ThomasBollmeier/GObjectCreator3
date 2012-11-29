from gobjcreator3.model.clsintf import ClsIntf
from gobjcreator3.model.type import Type

class GInterface(ClsIntf):
    
    def __init__(self, name):
        
        ClsIntf.__init__(self, name, Type.INTERFACE)
