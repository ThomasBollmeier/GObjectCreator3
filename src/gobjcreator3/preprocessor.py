from gobjcreator3.parser import GobjcreatorParser
import os
from bovinus.parser import AstNode

class PreProcessor(object):
    
    def __init__(self):
        
        self._parser = GobjcreatorParser()
        self._search_dirs = [os.curdir]
        self._search_dirs_std = self._search_dirs
        self._expanded_asts = {} 
        
    def get_expanded_ast(self, filepath):
        
        ast = self._parser.parseFile(filepath)
        
        new_children = []
        
        for child in ast.getChildren():
            if child.getName() != 'include':
                child.addChild(AstNode('origin', filepath))
                new_children.append(child)
            else:
                for inclpath in child.getChildren():
                    for new_child in self._resolve_include(inclpath):
                        new_children.append(new_child)
            
        ast.removeChildren()
        
        for child in new_children:
            ast.addChild(child)
            
        self._expanded_asts[filepath] = ast
                
        return ast
            
    def _resolve_include(self, include_path):
        
        filename = include_path['name'].getText()
        is_standard_include = bool(include_path['standard'])
        
        search_dirs = is_standard_include and self._search_dirs_std or self._search_dirs
        filepath = ""
        for search_dir in search_dirs:
            filepath = os.path.abspath(search_dir + os.sep + filename)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                break
            else:
                filepath = ""
                
        if not filepath or filepath in self._expanded_asts:
            return []
        
        included_ast = self.get_expanded_ast(filepath)
        
        return included_ast.getChildren() 
