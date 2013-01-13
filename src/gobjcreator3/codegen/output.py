import os

class AbstractOut(object):
    
    def __init__(self):
        pass
    
    def enter_dir(self, dir_path):
        
        pass
    
    def exit_dir(self, dir_path):
        
        pass
    
    def prepare_file_creation(self, file_path, template_processor):
        
        pass
    
    def visit_text_file(self, file_path, lines):
        
        pass
    
class StdOut(AbstractOut):
    
    def __init__(self):
        
        AbstractOut.__init__(self)
    
    def enter_dir(self, dir_path):
        
        print("Entering directory %s" % dir_path)
    
    def exit_dir(self, dir_path):
        
        print("Leaving directory %s" % dir_path)
    
    def visit_text_file(self, file_path, lines):
        
        print("File: %s" % file_path)
        for line in lines:
            print(line)
        print()
        print(80 * "-")
        print()
        
class FileOut(AbstractOut):
    
    def __init__(self, generation_root_dir):
        
        self._root_dir = os.path.abspath(generation_root_dir)
        
        if not os.path.exists(self._root_dir):
            os.mkdir(self._root_dir)
        
    def enter_dir(self, dir_path):
        
        if dir_path:
            complete_dir_path = self._root_dir + os.sep + dir_path
        else:
            complete_dir_path = self._root_dir
            
        if not os.path.exists(complete_dir_path):
            os.mkdir(complete_dir_path)
        
    def exit_dir(self, dir_path): 
        
        pass

    def prepare_file_creation(self, file_path, template_processor):
        
        complete_path = self._root_dir + os.sep + file_path
        
        template_processor.initEditableSections(complete_path)
    
    def visit_text_file(self, file_path, lines):
        
        complete_path = self._root_dir + os.sep + file_path
        
        f = open(complete_path, "w")
        for line in lines:
            f.write(line + os.linesep)
        f.close()
