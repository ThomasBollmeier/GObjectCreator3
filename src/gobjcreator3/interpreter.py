#from gobjcreator3.module import Module
from gobjcreator3.parameter import Parameter, BuiltIn, FullTypeName, ListOf, RefTo
from gobjcreator3.misc import Visibility, Scope

class Interpreter(object):
    
    def __init__(self):

        self._module = {"module": self._eval_module,
                        "type_declaration": self._eval_type_declaration,
                        "gobject": self._eval_gobject,
                        "ginterface": self._eval_ginterface,
                        "gerror": self._eval_gerror,
                        "genum": self._eval_genum,
                        "gflags": self._eval_gflags}
        
        self._top = {"include": self._eval_include}
        self._top.update(self._module)
        
        self._gobject = {"method_section": self._eval_method_section}
    
    def eval_grammar(self, ast, visitor):
        
        visitor.enter_grammar()
        
        for child in ast.getChildren():
            try:
                self._top[child.getName()](child, visitor)
            except KeyError:
                pass
        
        visitor.exit_grammar()
        
    def _eval_include(self, ast, visitor):
        
        for inclpath in ast.getChildren():
            visitor.visit_include_path(inclpath.getText())
            
    def _eval_module(self, ast, visitor):
        
        module_name = ast["name"].getText()
        
        visitor.enter_module(module_name)

        for child in ast.getChildren():
            try:
                self._module[child.getName()](child, visitor)
            except KeyError:
                pass
        
        visitor.exit_module()
        
    def _eval_type_declaration(self, ast, visitor):
        
        visitor.visit_type_declaration(ast.getText())
        
    def _eval_gobject(self, ast, visitor):
        
        name = ast["name"].getText()
        
        visitor.enter_gobject(name)

        for child in ast.getChildren():
            try:
                self._gobject[child.getName()](child, visitor)
            except KeyError:
                pass
        
        visitor.exit_gobject()
        
    def _eval_ginterface(self, ast, visitor):
        
        name = ast["name"].getText()
        
        visitor.enter_ginterface(name)
        
        visitor.exit_ginterface()        
        
    def _eval_gerror(self, ast, visitor):
        
        name = ast["name"].getText()
        
        codes = []
        for codeNode in ast.getChildrenByName('code'):
            codes.append(codeNode.getText())
        
        visitor.visit_gerror(name, codes)
                
    def _eval_genum(self, ast, visitor):
        
        name = ast["name"].getText()
        
        codeNamesValues = []
        for enumCodeNode in ast.getChildrenByName('enum_code'):
            cname = enumCodeNode['name'].getText()
            valueNode = enumCodeNode['value']
            value = valueNode and valueNode.getText() or None
            codeNamesValues.append((cname, value))
            
        visitor.visit_genum(name, codeNamesValues)

    def _eval_gflags(self, ast, visitor):
        
        name = ast["name"].getText()

        codes = []
        for codeNode in ast.getChildrenByName('code'):
            codes.append(codeNode.getText())
        
        visitor.visit_gflags(name, codes)
        
    def _eval_method_section(self, ast, visitor):
        
        visibility = {"public" : Visibility.PUBLIC,
                      "protected": Visibility.PROTECTED,
                      "private": Visibility.PRIVATE
                      }[ast["visibility"].getText()]
                
        for method in ast.getChildrenByName("method"):
            name = method["name"].getText()
            self._eval_method(method, visitor, name, visibility)
            
    def _eval_method(self, ast, visitor, name, visibility):
        
        props = ast["properties"]
        
        attributes = {"visibility": visibility}
        attributes["scope"] = props and props["static"] and Scope.CLASS or Scope.INSTANCE
        attributes["abstract"] = props and props["abstract"] and True or False
        attributes["overriden"] = props and props["overridden"] and True or False
        
        parameters = []
        
        for child in ast.getChildren():
            catg_name = child.getName()
            if catg_name == "in_param":
                category = Parameter.IN
                pname = child["name"].getText()
                argtype_node = child.getChildren()[1]
            elif catg_name == "inout_param":
                category = Parameter.IN_OUT
                pname = child["name"].getText()
                argtype_node = child.getChildren()[1]
            elif catg_name == "out_param":
                category = Parameter.OUT
                pname = ""
                argtype_node = child.getChildren()[0]
            else:
                continue
            argtype = self._eval_arg_type(argtype_node)
                        
            parameters.append(Parameter(pname, argtype, category))
        
        visitor.enter_method(name, attributes, parameters)
        
    def _eval_arg_type(self, argtype_node):
        
        name = argtype_node.getName()
        
        if name == "ref":
            ref_type = self._eval_arg_type(argtype_node.getChildren()[0])
            return RefTo(ref_type)
        elif name == "list":
            element_type = self._eval_arg_type(argtype_node.getChildren()[0])
            return ListOf(element_type)
        elif name == "full_type_name":
            return self._eval_full_type_name(argtype_node)
        elif name == "builtin_type":
            return BuiltIn(argtype_node.getText())
        else:
            raise Exception("Unknown type %s" % name)
        
    def _eval_full_type_name(self, full_type_name_node):
        
        name = full_type_name_node['name'].getText()
        
        module_path = []
        for child in full_type_name_node.getChildrenByName('module'):
            module_path.append(child.getText())
            
        is_absolute_type = bool(full_type_name_node['absolute_type'])
        
        return FullTypeName(name, module_path, is_absolute_type)
