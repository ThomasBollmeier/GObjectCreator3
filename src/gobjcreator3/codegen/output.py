class AbstractOut(object):
    
    def __init__(self):
        pass
    
    def enter_dir(self, dir_path):
        
        pass
    
    def exit_dir(self, dir_path):
        
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
