class PropGTypeInfo(object):
    
    def __init__(self):
        
        self.gtype_id = ""
        self.full_type_name = None
        
    def __str__(self):
        
        if self.gtype_id:
            return self.gtype_id
        else:
            return "GType of %s" % self.full_type_name