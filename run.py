# 1. load templates
# 2. fill any nested templates
# 3. load html files
# 4. fill templates in html files
# 5. write updated html to output directory

import os, sys, json, bs4
from HtmlWrapper import HtmlWrapper
from Template import Template
import TemplateLoader as TL
from bs4 import BeautifulSoup
import shutil

htmlFiles = []
templates = []

outputDir = "output"

if "-c" in sys.argv:
    configPath = sys.argv[sys.argv.index("-c") + 1]
elif "--config" in sys.argv:
    configPath = sys.argv[sys.argv.index("--config") + 1]
else:
    configPath = "./config.json"


def loadConfigFile(path):
    # check if file exists
    if not os.path.isfile(path):
        return {}
    # read
    try:
        with open(path, "r") as file:
            config = json.load(file)
        return config

    except json.decoder.JSONDecodeError:
        print("Error: config file is not valid json")
        return {}


config = loadConfigFile(configPath)


def getAllHtmlFilesToProcess(path, folderExclusion=[], fileExclusions=[]):
    htmlFiles = []
    for root, dirs, files in os.walk(path):
        # TODO implement folderExclusion
        for file in files:
            if file.endswith(".html") and not file in fileExclusions:
                obj = HtmlWrapper()
                obj.path = os.path.join(root, file)
                htmlFiles.append(obj)
    return htmlFiles


def getAllTemplatesToProcess(path, folderExclusion=[], fileExclusions=[]):
    ts = []
    for root, dirs, files in os.walk(path):
        # TODO implement folderExclusion
        for file in files:
            if file.endswith(".tml") and not file in fileExclusions:
                obj = Template()
                obj.path = os.path.join(root, file)
                ts.append(obj)
    return ts


htmlRoot = sys.argv[1] if len(sys.argv) > 1 else "."
tmlFolder = sys.argv[2] if len(sys.argv) > 2 else "."
htmlFiles = getAllHtmlFilesToProcess(htmlRoot)
templates = getAllTemplatesToProcess(tmlFolder)


def loadHtmlFiles(htmlWrappers):
    for obj in htmlWrappers:
        with open(obj.path, "r", encoding="utf8") as file:
            obj.content = file.read()


def loadTemplates(ts):
    for i, template in enumerate(ts):
        with open(template.path, "r") as file:
            t = TL.parseTemplate(file.read())
        t.path = template.path
        ts[i] = t


loadHtmlFiles(htmlFiles)
loadTemplates(templates)


def findHtmlDependencies(h, templates):
    for t in templates:
        if "<" + t.id in h.content:
            h.dependencies.add(t.id)


for t in templates:
    t.dependencies = TL.findDependencies(t, templates)

for h in htmlFiles:
    findHtmlDependencies(h, templates)

# create topological sort of templates and html files (checking for a cycle as well)
# for each template, find all html files that depend on it
dependsOn = {}
for h in htmlFiles:
    dependsOn[h.path] = h.dependencies
for t in templates:
    dependsOn[t.id] = t.dependencies

dependedOnBy = {}
for key in dependsOn:
    for value in dependsOn[key]:
        if value in dependedOnBy:
            dependedOnBy[value].append(key)
        else:
            dependedOnBy[value] = [key]

# print("\n".join([str(x) for x in dependsOn.items()]))
# print("\n".join([str(x) for x in dependedOnBy.items()]))


# https://www.geeksforgeeks.org/topological-sorting-indegree-based-solution/
def topologicalSort(graph):

    # Create a vector to store in-degrees of all vertices. Initialize all indegrees as 0.
    indegree = {i: 0 for i in graph.keys()}

    # Traverse adjacency lists to fill in-degrees of vertices.
    for i in graph:
        for j in graph[i]:
            indegree[j] += 1

    # Create an queue and enqueue all vertices with indegree 0
    queue = [x for x in graph.keys() if indegree[x] == 0]

    visitedCount = 0
    top_order = []

    while queue:

        # dequeue and add to topological order
        u = queue.pop(0)
        top_order.append(u)

        # Iterate through all neighbouring nodes of dequeued node u and decrease their in-degree by 1
        for i in graph[u]:
            indegree[i] -= 1
            # If in-degree becomes zero, add it to queue
            if indegree[i] == 0:
                queue.append(i)

        visitedCount += 1

    if visitedCount != len(graph.keys()):
        print("There exists a cycle in the graph")
        return None
    else:
        return top_order


# print ("Following is a Topological Sort of the given graph")
topsort = topologicalSort(dependsOn)
topsort.reverse()
# print(topsort)

# fill templates and html in topological order

TEMPLATE_VAR_START = "{{"
TEMPLATE_VAR_END = "}}"


def fillTemplate(template, variables):
    html = template.content
    for v in template.variables:
        if v in variables:
            html = html.replace(TEMPLATE_VAR_START + v + TEMPLATE_VAR_END, variables[v])
        else:
            html = html.replace(
                TEMPLATE_VAR_START + v + TEMPLATE_VAR_END, template.defaults[v]
            )
    return html


def fillFile(file, templates):
    templateIds = [t.id for t in templates]
    soup = BeautifulSoup(file.content, "html.parser")
    elem = soup.find()
    while elem != None:
        nextelem = elem.findNext()
        if elem.name in templateIds:
            t = next(t for t in templates if t.id == elem.name)
            newelem = BeautifulSoup(fillTemplate(t, elem.attrs), "html.parser")
            elem.replace_with(newelem)
        elem = nextelem
    file.content = soup.prettify(formatter=bs4.formatter.HTMLFormatter(indent=4))
 
 
for t in topsort:
    item = next((x for x in templates if x.id == t), None)
    if not item:
        item = next((x for x in htmlFiles if x.path == t), None)
    fillFile(item, templates)
    # print(item.content)

# write updated html to output directory
# set ouput directory root

os.umask(0o077)

# TODO implement file and folder copying exclusion
shutil.copytree(htmlRoot, outputDir, dirs_exist_ok=True)

for h in htmlFiles:
    # set path to replace input directory with output directory
    path = h.path.replace(htmlRoot, outputDir)
    print(os.path.dirname(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(h.content)
