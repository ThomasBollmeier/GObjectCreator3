from gobjcreator3.parameter import Parameter, BuiltIn, FullTypeName, ListOf, RefTo
from gobjcreator3.misc import PropGTypeInfo, PropValue, PropNumberInfo, PropCodeInfo
from gobjcreator3.model.visibility import Visibility
from gobjcreator3.model.property import PropType, PropAccess
 
class Interpreter(object):
    
    def __init__(self):

        self._top = {"module": self._eval_module,
                     "type_declaration": self._eval_type_declaration,
                     "gobject": self._eval_gobject,
                     "ginterface": self._eval_ginterface,
                     "gerror": self._eval_gerror,
                     "genum": self._eval_genum,
                     "gflags": self._eval_gflags}
        
        self._module = self._top
        
        self._gobject = {"method_section": self._eval_method_section,
                         "attr_section": self._eval_attr_section,
                         "properties": self._eval_properties,
                         "signals": self._eval_signals
                         }

        self._visi_map = {"public" : Visibility.PUBLIC,
                          "protected": Visibility.PROTECTED,
                          "private": Visibility.PRIVATE
                          }
        
        self._prop_type_map = {"boolean": PropType.BOOLEAN,
                               "byte": PropType.BYTE,
                               "integer": PropType.INTEGER,
                               "float": PropType.FLOAT,
                               "double": PropType.DOUBLE,
                               "string": PropType.STRING,
                               "pointer": PropType.POINTER,
                               "object": PropType.OBJECT,
                               "enumeration": PropType.ENUMERATION
                               }
        
        self._prop_access_map = {"read-only": PropAccess.READ_ONLY,
                                 "initial-write": PropAccess.INITIAL_WRITE,
                                 "read-write": PropAccess.READ_WRITE
                                 }
        
        self._cur_class_name = ""
    
    def eval_grammar(self, ast, visitor):
        
        self._cur_origin = ""
        
        visitor.enter_grammar()
        
        for child in ast.getChildren():
            self._top[child.getName()](child, visitor)
        
        visitor.exit_grammar()
        
    def _eval_module(self, ast, visitor):
        
        module_name = ast["name"].getText()
        
        self._refresh_origin(ast)
                
        visitor.enter_module(module_name, self._cur_origin)

        for child in ast.getChildren():
            try:
                self._module[child.getName()](child, visitor)
            except KeyError:
                pass
        
        visitor.exit_module()
        
    def _eval_type_declaration(self, ast, visitor):
        
        self._refresh_origin(ast)

        visitor.visit_type_declaration(ast.getText(), self._cur_origin)
        
    def _eval_gobject(self, ast, visitor):
        
        name = ast["name"].getText()
        
        self._cur_class_name = name
        
        self._refresh_origin(ast)

        super_class_node = ast["super_class"]
        if not super_class_node:
            super_class = None
        else:
            super_class = self._eval_super_class(super_class_node)
            
        interfaces = []
        
        for intfsNode in ast.getChildrenByName("interfaces"):
            for intfNode in intfsNode.getChildren():
                if intfNode.getName() == "full_type_name":
                    interfaces.append(self._eval_full_type_name(intfNode))
                else:
                    interfaces.append(BuiltIn(intfNode.getText()))
        
        cfunc_prefix = ""
        for prefix_node in ast.getChildrenByName("cfunc_prefix"):
            cfunc_prefix = prefix_node.getText()
            break
        
        is_abstract = bool(ast["abstract"])
        is_final = bool(ast["final"])
        
        visitor.enter_gobject(name,
                              is_abstract,
                              is_final, 
                              super_class, 
                              interfaces, 
                              cfunc_prefix, 
                              self._cur_origin
                              )

        for child in ast.getChildren():
            try:
                self._gobject[child.getName()](child, visitor)
            except KeyError:
                pass
        
        visitor.exit_gobject()
        
        self._cur_class_name = ""
        
    def _eval_super_class(self, super_class_node):
        
        super_type = super_class_node.getChildren()[0]
        
        if super_type.getName() == "full_type_name":
            return self._eval_full_type_name(super_type)
        else:
            return BuiltIn(super_type.getText())
        
    def _eval_ginterface(self, ast, visitor):
        
        name = ast["name"].getText()
        
        self._refresh_origin(ast)

        cfunc_prefix = ""
        for prefix_node in ast.getChildrenByName("cfunc_prefix"):
            cfunc_prefix = prefix_node.getText()
            break
                
        visitor.enter_ginterface(name, cfunc_prefix, self._cur_origin)
        
        for method in ast.getChildrenByName("interface_method"):
            self._eval_interface_method(method, visitor)
        
        visitor.exit_ginterface()
        
    def _eval_interface_method(self, method, visitor):
        
        name = method['name'].getText()
        
        parameters = self._get_method_parameters(method)
            
        visitor.visit_interface_method(name, parameters)
        
    def _eval_gerror(self, ast, visitor):
        
        name = ast["name"].getText()
        
        self._refresh_origin(ast)
                
        codes = []
        for codeNode in ast.getChildrenByName('code'):
            codes.append(codeNode.getText())
        
        visitor.visit_gerror(name, codes, self._cur_origin)
                
    def _eval_genum(self, ast, visitor):
        
        name = ast["name"].getText()
        
        self._refresh_origin(ast)
                
        codeNamesValues = []
        for enumCodeNode in ast.getChildrenByName('enum_code'):
            cname = enumCodeNode['name'].getText()
            valueNode = enumCodeNode['value']
            value = valueNode and valueNode.getText() or None
            codeNamesValues.append((cname, value))
            
        visitor.visit_genum(name, codeNamesValues, self._cur_origin)

    def _eval_gflags(self, ast, visitor):
        
        name = ast["name"].getText()
        
        self._refresh_origin(ast)
        
        codes = []
        for codeNode in ast.getChildrenByName('code'):
            codes.append(codeNode.getText())
        
        visitor.visit_gflags(name, codes, self._cur_origin)
        
    def _eval_method_section(self, ast, visitor):
        
        visibility = self._visi_map[ast["visibility"].getText()]
                
        for method in ast.getChildrenByName("method"):
            name = method["name"].getText()
            self._eval_method(method, visitor, name, visibility)
            
    def _eval_method(self, ast, visitor, name, visibility):
        
        props = ast["properties"]
        
        attributes = {"visibility": visibility}
        attributes["static"] = props and props["static"] and True or False
        attributes["abstract"] = props and props["abstract"] and True or False
        attributes["overridden"] = props and props["overridden"] and True or False
        attributes["final"] = props and props["final"] and True or False
        attributes["constructor"] = ( name == 'constructor' or name == self._cur_class_name ) 
        
        parameters = self._get_method_parameters(ast)

        visitor.visit_method(name, attributes, parameters)
        
    def _get_method_parameters(self, method):
        
        parameters = []
        
        for child in method.getChildren():
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
                
            param = Parameter(pname, argtype, category)
            
            props = child["properties"]
            if props:
                for p in props.getChildren():
                    param_prop_name = p.getName()
                    param.properties[param_prop_name] = {
                                                         "const" : True
                                                         }[param_prop_name]
                
            parameters.append(param)
            
        return parameters
        
    def _eval_attr_section(self, ast, visitor):
        
        visibility = self._visi_map[ast["visibility"].getText()]
                
        for attr in ast.getChildrenByName("attribute"):
            name = attr["name"].getText()
            self._eval_attribute(attr, visitor, name, visibility)
            
    def _eval_attribute(self, attr, visitor, name, visibility):
        
        props = attr["properties"]  
        aattrs = {"visibility": visibility}
        aattrs["static"] = props and props["static"] and True or False
        
        type_node = attr.getChildren()[1]
        if type_node.getName() == "builtin_type":
            atype = BuiltIn(type_node.getText())
        else:
            atype = self._eval_full_type_name(type_node)
        
        visitor.visit_attribute(name, atype, aattrs)
        
    def _eval_properties(self, ast, visitor):
        
        for propNode in ast.getChildren():
            name = ""
            attrs = {} 
            for child in propNode.getChildren():
                cname = child.getName()
                if cname == "name":
                    name = child.getText()
                elif cname == "type":
                    attrs["type"] = self._prop_type_map[child.getText()]
                elif cname == "access":
                    attrs["access"] = self._prop_access_map[child.getText()]
                elif cname == "description":
                    attrs["description"] = child.getText()
                elif cname == "gtype":
                    attrs["gtype"] = self._eval_prop_gtype(child)
                elif cname in ["min", "max", "default"]:
                    attrs[cname] = self._eval_prop_value(child)
                elif cname == "auto-create":
                    attrs["auto-create"] = True
            visitor.visit_property(name, attrs)
            
    def _eval_prop_gtype(self, ast):
        
        res = PropGTypeInfo()
        
        type_of_node = ast["type_of"]
        if type_of_node:
            type_node = type_of_node.getChildren()[0]
            if type_node.getName() == "full_type_name":
                res.full_type_name = self._eval_full_type_name(type_node)
            else:
                res.full_type_name = BuiltIn(type_node.getText())
        else:
            res.g_type_id = ast["id"].getText() 
        
        return res
    
    def _eval_prop_value(self, ast):
        
        value = PropValue()
        
        value_node = ast.getChildren()[0]
        name = value_node.getName()
        
        if name == "literal":
            value.literal = value_node.getText()
        elif name == "number":
            digits = value_node['digits'].getText()
            decimals_node = value_node['decimals']
            decimals = decimals_node and decimals_node.getText() or None
            value.number_info = PropNumberInfo(digits, decimals)
        elif name == "code_value":
            enumeration_name = self._eval_full_type_name(value_node['full_type_name'])
            code_name = value_node['code'].getText()
            value.code_info = PropCodeInfo(enumeration_name, code_name)
            
        return value 
                            
    def _eval_signals(self, ast, visitor):
        
        for signalNode in ast.getChildrenByName("signal"):
            name = signalNode["name"].getText()
            parameters = self._get_method_parameters(signalNode)
            visitor.visit_signal(name, parameters)
                    
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
    
    def _refresh_origin(self, ast):
        
        originNode = ast['origin']
        if originNode:
            self._cur_origin = originNode.getText() 
