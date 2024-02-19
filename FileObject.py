class FileObject:
    def __init__(self):
        self.path = ""
        self.content = ""
        self.dependencies = set()
        self.lastProcessed = 0 # time in ns since epoch
        
    def __str__(self):
        return "FileObject: " + self.path
    
    def __repr__(self):
        return "FileObject: " + self.path