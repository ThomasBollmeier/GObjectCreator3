import unittest

from gobjcreator3.model.module import RootModule 

class ModelTest(unittest.TestCase):
    
    def setUp(self):
        
        pass
                    
    def tearDown(self):
        
        pass
        
    def testModule(self):
        
        root = RootModule()
           
        widgets = root.get_module('ui::widgets')
        utils = root.get_module('ui::utils')
        ui = root.get_module('ui')
        
        self.assertEqual(root.modules, [ui])    
        self.assertEqual(len(root._instances), 3)
        self.assertEqual(widgets.module, ui)
        self.assertEqual(utils.module, ui)
            
        num_modules = len(ui.modules)
        self.assertEqual(num_modules, 2, "Number of modules differs (expected: 2, actual: %d" % num_modules)
                          
if __name__ == "__main__":
    
    unittest.main()

