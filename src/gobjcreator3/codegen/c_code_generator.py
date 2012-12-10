from gobjcreator3.codegen.code_generator import CodeGenerator

class CCodeGenerator(CodeGenerator):
    
    def __init__(self, root_module, origin):
        
        CodeGenerator.__init__(self, root_module, origin)
        
    def generate(self):
        
        self._generate_module(self.root_module)
        
    def _generate_module(self, module):
        
        for m in module.modules:
            self._generate_module(m)
        
        objs = [obj for obj in module.objects if obj.filepath_origin == self.origin]
        
        for obj in objs:
            print("GObject: %s" % obj.name)        
        
        