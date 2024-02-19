from FileObject import FileObject

# Class that represents a TML template
class Template(FileObject):
    def __init__(self):
        super(Template, self).__init__()
        self.defaults = {}
        self.variables = []
        self.id = "" # how the template will be referenced in the HTML files, e.g. <id></id>
                     # cannot contain spaces or special characters or be a reserved HTML word
    
    def __str__(self):
        return "Template: " + self.id + " " + self.path
    
    def __repr__(self):
        return "Template: " + self.id + " " + self.path