from gobjcreator3.codegen.output import StdOut

class CodeGenerator(object):
    
    def __init__(self, root_module, origin, out=StdOut()):
        
        self._root_module = root_module
        self._origin = origin
        self._out = out
        
    def generate(self):
        
        pass
    