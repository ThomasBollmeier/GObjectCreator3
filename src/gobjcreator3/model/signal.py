from gobjcreator3.model.method import Method
from gobjcreator3.model.visibility import Visibility

class Signal(Method):
    
    def __init__(self, name, parameters):
        
        Method.__init__(self, name)
        
        self.parameters = parameters
        self.visibility = Visibility.PUBLIC
        self.set_abstract(True)
        self.set_static(False)