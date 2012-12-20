class AstVisitor(object):
    
    def __init__(self):
        pass
    
    def enter_grammar(self):
        pass
    
    def exit_grammar(self):
        pass
    
    def enter_module(self, module_name, origin):
        pass
    
    def exit_module(self):
        pass
    
    def visit_type_declaration(self, typename, origin):
        pass

    def enter_gobject(self, 
                      name,
                      is_abstract,
                      is_final,
                      super_class,
                      interfaces,
                      cfunc_prefix,
                      origin
                      ):
        pass
    
    def exit_gobject(self):
        pass
    
    def enter_ginterface(self, name, cfunc_prefix, origin):
        pass
    
    def exit_ginterface(self):
        pass    
    
    def visit_gerror(self, name, codes, origin):
        pass
    
    def visit_genum(self, name, codeNamesValues, origin):
        pass
    
    def visit_gflags(self, name, codes, origin):
        pass
    
    def visit_method(self, 
                     name, 
                     attributes,
                     parameters,
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
    
    def visit_property(self,
                       name,
                       attributes
                       ):
        
        pass
    
    def visit_signal(self,
                     name,
                     parameters
                     ):
        pass
