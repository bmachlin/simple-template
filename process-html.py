from TemplateLoader import TemplateLoader, fillTemplate
from bs4 import BeautifulSoup
import bs4


def processHTMLFile(filepath, templates):
    print("Processing file:", filepath)
    with open(filepath, "r") as file:
        soup = BeautifulSoup(file, 'html.parser')
    fillTemplates(soup, templates)
    print(soup.prettify())
    return soup

# find and fill in templates within html
def fillTemplates(soup, templates):
    templateNames = templates.keys()
    dependencies = set()
    # start with first element
    elem = soup.find()
    while elem != None:
        nextelem = elem.findNext()
        if elem.name in templateNames:
            dependencies.add(elem.name)
            template = templates[elem.name]
            newelem = BeautifulSoup(fillTemplate(template, elem.attrs), "html.parser")
            elem.replace_with(newelem)
        elem = nextelem

# templates = TemplateLoader("C:/Users/ben/Coding/bmachlin/templates").getAll()
# output = processHTMLFile("test/test-parser.html", templates)
# with open("test/test-parser-output.html", "w") as file:
#     file.write(output.prettify(formatter=bs4.formatter.HTMLFormatter(indent=4)))
