import os

class IncludeDirs(object):
    
    def __init__(self):
        
        self._search_path = [os.curdir]
        self._search_path_std = self._search_path
        
    def get_abs_filepath(self, include_path, is_standard):
        
        if not is_standard:
            search_dirs = self._search_path
        else:
            search_dirs = self._search_path_std
            
        for search_dir in search_dirs:
            path = search_dir + os.sep + include_path
            path = os.path.abspath(path)
            if os.path.exists(path) and os.path.isfile(path):
                return path
            
        raise Exception("Could not find include file '%s'!" % include_path)
            
            
        
        