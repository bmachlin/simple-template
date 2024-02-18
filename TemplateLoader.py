import os
from Template import Template
from pprint import pprint
from bs4 import BeautifulSoup

TEMPLATE_SECTION_SPLIT = "\n%\n"
TEMPLATE_VAR_START = "{{"
TEMPLATE_VAR_END = "}}"


# parse template object from file data
def parseTemplate(data):
    template = Template()
    parts = data.split(TEMPLATE_SECTION_SPLIT, maxsplit=2)
    
    template.id = parts[0].strip()
    
    # 3 parts means id -> defaults -> content
    # 2 parts means id -> content
    if len(parts) >= 3:
        template.defaults = parseTemplateDefaults(parts[1])
        template.content = parts[2]
    else:
        template.content = parts[1]
        
    template.variables = parseTemplateVars(template.content)
    
    return template


# defaults specified one on each line with = separator
def parseTemplateDefaults(data):
    defaults = {}
    # split defaults by newline
    for line in data.split("\n"):
        # split default name and value by '='
        parts = line.split("=", 1)
        if len(parts) == 2:
            defaults[parts[0].strip()] = parts[1].strip()
    return defaults


# find all the {{variables}} in the template
def parseTemplateVars(templateString):
    variables = []
    for i in range(len(templateString)):
        # find the start of a variable
        if templateString[i:i+len(TEMPLATE_VAR_START)] == TEMPLATE_VAR_START:
            start = i
            # find the end of the variable
            end = templateString.find(TEMPLATE_VAR_END, start) + len(TEMPLATE_VAR_END)
            # add the variable to the list sans variable syntax
            variables.append(templateString[start + len(TEMPLATE_VAR_START) : end - len(TEMPLATE_VAR_END)])
    return variables


def findDependencies(template, allTemplates):
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
    

def fillTemplate(template, variables):
    html = template.content
    for v in template.variables:
        if v in variables:
            html = html.replace(TEMPLATE_VAR_START + v + TEMPLATE_VAR_END, variables[v])
        else:
            html = html.replace(TEMPLATE_VAR_START + v + TEMPLATE_VAR_END, template.defaults[v])
    return html


# tl = TemplateLoader("C:/Users/ben/Coding/bmachlin/templates")
# pprint(fillTemplate(tl.get("navbar"), {"text": "Hello World"}))