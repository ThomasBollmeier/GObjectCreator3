class AstVisitor(object):
    
    def __init__(self):
        pass
    
    def enter_grammar(self):
        pass
    
    def exit_grammar(self):
        pass
    
    def visit_include_path(self, include_path):
        pass
    
    def enter_module(self, module_name):
        pass
    
    def exit_module(self):
        pass
    
    def visit_type_declaration(self, typename):
        pass

    def enter_gobject(self, 
                      name,
                      super_class,
                      interfaces
                      ):
        pass
    
    def exit_gobject(self):
        pass
    
    def enter_ginterface(self, name):
        pass
    
    def exit_ginterface(self):
        pass    
    
    def visit_gerror(self, name, codes):
        pass
    
    def visit_genum(self, name, codeNamesValues):
        pass
    
    def visit_gflags(self, name, codes):
        pass
    
    def visit_method(self, 
                     name, 
                     attributes,
                     parameters 
                     ):
        pass
    
    def visit_interface_method(self,
                               name,
                               parameters
                               ):
        pass
    
    def visit_attribute(self,
                        aname,
                        atype,
                        aattributes
                        ):
        pass
