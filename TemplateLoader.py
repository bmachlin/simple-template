import os
from Template import Template
from pprint import pprint
from bs4 import BeautifulSoup

class TemplateLoader:
    def __init__(self):
        self.TEMPLATE_SECTION_SPLIT = "\n%\n"
        self.TEMPLATE_VAR_START = "{{"
        self.TEMPLATE_VAR_END = "}}"
        self.INNER_HTML_VAR = "_inner_"
        

    # parse template object from file data
    def ParseTemplate(self, data):
        template = Template()
        parts = data.split(self.TEMPLATE_SECTION_SPLIT, maxsplit=2)
        
        template.id = parts[0].strip()
        
        # 3 parts means id -> defaults -> content
        # 2 parts means id -> content
        if len(parts) >= 3:
            template.defaults = self.ParseTemplateDefaults(parts[1])
            template.content = parts[2]
        else:
            template.content = parts[1]
            
        template.variables = self.ParseTemplateVars(template.content)
        
        return template


    # defaults specified one on each line with = separator
    def ParseTemplateDefaults(self, data):
        defaults = {}
        
        # split defaults by newline
        for line in data.split("\n"):
            # split default name and value by '='
            parts = line.split("=", 1)
            if len(parts) == 2:
                defaults[parts[0].strip()] = parts[1].strip()
                
        return defaults


    # find all the {{variables}} in the template
    def ParseTemplateVars(self, templateString):
        variables = []
        
        for i in range(len(templateString)):
            # find the start of a variable
            if templateString[i:i+len(self.TEMPLATE_VAR_START)] == self.TEMPLATE_VAR_START:
                start = i
                # find the end of the variable
                end = templateString.find(self.TEMPLATE_VAR_END, start) + len(self.TEMPLATE_VAR_END)
                # add the variable to the list sans variable syntax
                variables.append(templateString[start + len(self.TEMPLATE_VAR_START) : end - len(self.TEMPLATE_VAR_END)])
                
        return variables


    def FindDependencies(self, template, allTemplates):
        dependencies = set()
        soup = BeautifulSoup(template.content, 'html.parser')
        templateIds = [t.id for t in allTemplates]
        elem = soup.find()
        
        while elem != None:
            nextelem = elem.findNext()
            if elem.name in templateIds:
                dependencies.add(elem.name)
            elem = nextelem
            
        return dependencies
        

    def FillTemplate(self, template, variables):
        html = template.content
        
        for v in template.variables:
            if v in variables:
                html = html.replace(self.TEMPLATE_VAR_START + v + self.TEMPLATE_VAR_END, variables[v])
            else:
                html = html.replace(self.TEMPLATE_VAR_START + v + self.TEMPLATE_VAR_END, template.defaults[v])
                
        return html