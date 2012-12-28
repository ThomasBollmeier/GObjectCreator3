from gobjcreator3.model.method import Method, Parameter
from gobjcreator3.model.visibility import Visibility

class Signal(Method):
    
    def __init__(self, name, parameters):
        
        Method.__init__(self, name)
        
        self.parameters = parameters
        self.visibility = Visibility.PUBLIC
        self.set_abstract(True)
        self.set_static(False)
        
    def get_input_params(self):
        
        return [p for p in self.parameters if p.direction != Parameter.OUT]
