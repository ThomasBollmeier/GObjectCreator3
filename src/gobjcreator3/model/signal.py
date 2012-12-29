from gobjcreator3.model.method import Method, Parameter
from gobjcreator3.model.visibility import Visibility

class Signal(Method):
    
    def __init__(self, name, parameters, has_default_handler):
        
        Method.__init__(self, name)
        
        self.has_default_handler = has_default_handler
        self.parameters = parameters
        self.visibility = Visibility.PUBLIC
        self.set_abstract(True)
        self.set_static(False)
        
    def get_input_params(self):
        
        return [p for p in self.parameters if p.direction != Parameter.OUT]
