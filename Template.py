# Class that represents a TML template
class Template:
    def __init__(self):
        self.path = ""
        self.id = "" # how the template will be referenced in the HTML files, e.g. <id></id>
                     # cannot contain spaces or special characters or be a reserved HTML word
        self.content = ""
        self.defaults = {}
        self.variables = []
        self.dependencies = []
    