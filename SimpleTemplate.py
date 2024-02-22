import os, json, time, shutil, bs4
from fnmatch import fnmatch
from bs4 import BeautifulSoup
from FileObject import FileObject
from Template import Template
from TemplateLoader import TemplateLoader
import Dependencies


class SimpleTemplate:
    def __init__(self, config=None, configPath=None):
        self.firstPass = False
        self.htmlFiles = []
        self.templates = []
        self.processOrder = []
        self.TemplateLoader = TemplateLoader()

        # default config options
        self.config = {
            "TEMPLATE_VAR_START": "{{",
            "TEMPLATE_VAR_END": "}}",
            "TEMPLATE_SECTION_SPLIT": "\n%\n",
            "EMPTY_VAR_REPLACE": True,
            "EMPTY_VAR_VALUE": "",
            "INPUT_DIR": ".",
            "OUTPUT_DIR": "output",
            "TEMPLATE_DIR": "templates",
            "EXCLUDE_ALL": [],
            "EXCLUDE_HTML": [],
            "EXCLUDE_TEMPLATE": [],
            "EXCLUDE_COPY": [],
            "OVERWRITE_ALLOWED": False,
        }

        # apply zero, one, or both config options
        if configPath is not None:
            self.LoadConfigFromPath(configPath)
        if config is not None:
            self.LoadConfig(config)

    ########## CONFIG ##########
    
    def ShouldExclude(self, excludePatterns, fp):
        for pattern in excludePatterns:
            if fnmatch(fp, pattern):
                print("Excluding", fp, "because of", pattern)
                return True
        return False

    # Loads and applies a config file given a path
    def LoadConfigFromPath(self, path):
        if not os.path.isfile(path):
            return

        try:
            with open(path, "r") as file:
                config = json.load(file)
            self.LoadConfig(config)

        except json.decoder.JSONDecodeError:
            print("Error: config file is not valid json")
            return

    # Loads and applies a config object
    def LoadConfig(self, config):
        for key in self.config.keys():
            if key in config:
                self.config[key] = config[key]

    def SetInputDir(self, path):
        self.config["INPUT_DIR"] = path

    def SetOutputDir(self, path):
        self.config["OUTPUT_DIR"] = path

    def SetTemplateDir(self, path):
        self.config["TEMPLATE_DIR"] = path

    ########## FILE LOADING ##########

    def GetHtmlFilePaths(self):
        fps = []
        excludePatters = self.config["EXCLUDE_ALL"] + self.config["EXCLUDE_HTML"]
        for root, dirs, files in os.walk(self.config["INPUT_DIR"]):
            for file in files:
                fp = os.path.normpath(os.path.join(root, file))
                if file.endswith(".html") and not self.ShouldExclude(excludePatters, fp):
                    print("Loading html", fp)
                    obj = FileObject()
                    obj.path = fp
                    fps.append(obj)
        return fps

    def GetTemplateFilePaths(self):
        fps = []
        excludePatters = self.config["EXCLUDE_ALL"] + self.config["EXCLUDE_TEMPLATE"]
        for root, dirs, files in os.walk(self.config["TEMPLATE_DIR"]):
            for file in files:
                fp = os.path.normpath(os.path.join(root, file))
                if file.endswith(".tml") and not self.ShouldExclude(excludePatters, fp):
                    print("Loading tml", fp)
                    obj = Template()
                    obj.path = fp
                    fps.append(obj)
        return fps

    def LoadHtmlFiles(self):
        fps = self.GetHtmlFilePaths()
        for obj in fps:
            try:
                with open(obj.path, "r", encoding="utf8") as file:
                    obj.content = file.read()
                self.htmlFiles.append(obj)
            except Exception as e:
                print("Error: could not read file " + obj.path)
                print(e)

    def LoadTemplates(self):
        fps = self.GetTemplateFilePaths()
        for obj in fps:
            try:
                with open(obj.path, "r", encoding="utf8") as file:
                    data = file.read()
                t = self.TemplateLoader.ParseTemplate(data)
                t.path = obj.path
                self.templates.append(t)
            except Exception as e:
                print("Error: could not read file " + obj.path)
                print(e)

    ########## DEPENDENCIES ##########

    def FindHtmlDependencies(self):
        for h in self.htmlFiles:
            for t in self.templates:
                # TODO probably want to make this more robust
                if "<" + t.id in h.content:
                    h.dependencies.add(t.id)

    def FindTemplateDependencies(self):
        for t in self.templates:
            for t2 in self.templates:
                if t.id == t2.id:
                    continue
                # TODO probably want to make this more robust
                if "<" + t2.id in t.content:
                    t.dependencies.add(t2.id)

    def TopologicalSort(self):
        self.processOrder = Dependencies.TopologicalSort(self.htmlFiles, self.templates)

    ########## FILLING ##########

    def FillTemplate(self, template, variables):
        content = template.content

        for v in template.variables:
            value = None
            if v in variables:
                value = variables[v]
            elif template.defaults is not None and v in template.defaults:
                value = template.defaults[v]
            elif self.emptyVarReplace:
                value = self.emptyVarValue

            # replace the variable with the value if it exists
            if value is not None:
                content = content.replace(self.config["TEMPLATE_VAR_START"] + v + self.config["TEMPLATE_VAR_END"], value)

        print(template.id)
        if template.id == "navbar":
            print(content)
        return content

    def FillFile(self, file):
        # TODO is there a better way to do this? possibly without using bs4?
        templateIds = [t.id for t in self.templates]
        soup = BeautifulSoup(file.content, "html.parser")
        elem = soup.find()
        # iterate all elements
        while elem != None:
            nextelem = elem.findNext()
            # replace template tags with their filled content
            if elem.name in templateIds:
                t = next(t for t in self.templates if t.id == elem.name)
                newelem = BeautifulSoup(self.FillTemplate(t, elem.attrs), "html.parser")
                elem.replace_with(newelem)
            elem = nextelem

        file.content = soup.prettify(formatter="html")
        file.lastProcessed = time.time_ns()

    def FillAllFiles(self):
        for t in self.processOrder:
            item = next((x for x in self.templates if x.id == t), None)
            if not item:
                item = next((x for x in self.htmlFiles if x.path == t), None)
            self.FillFile(item)

    ########## OUTPUT ##########

    def CopyInputDirectory(self):
        excludePatterns = self.config["EXCLUDE_ALL"] + self.config["EXCLUDE_COPY"]
        def excludeFn(path, names):
            excluded = []
            for name in names:
                fp = os.path.join(os.path.normpath(path), name)
                if os.path.isdir(fp):
                    fp += "/"
                if self.ShouldExclude(excludePatterns, fp):
                    excluded.append(name)
            return excluded
        
        print("will copy", self.config["INPUT_DIR"], "to", self.config["OUTPUT_DIR"])
        shutil.copytree(self.config["INPUT_DIR"], self.config["OUTPUT_DIR"], dirs_exist_ok=True, ignore=excludeFn)

    def CopyFile(self, fp):
        excludePatterns = self.config["EXCLUDE_ALL"] + self.config["EXCLUDE_COPY"]
        if not self.ShouldExclude(excludePatterns, fp):
            newFp = fp.replace(self.config["INPUT_DIR"], self.config["OUTPUT_DIR"])
            shutil.copy(fp, newFp)
        

    def OutputProcessedFiles(self):
        # print("Outputting processed files to", self.outputRoot)
        # os.umask(0o077) # do I need this?
        for h in self.htmlFiles:
            # skip outputting files that have no dependencies, i.e. were not changed
            if not h.dependencies:
                continue
            # set path to replace input directory with output directory
            path = h.path.replace(os.path.normpath(self.config["INPUT_DIR"]), os.path.normpath(self.config["OUTPUT_DIR"]))
            print("will write", h.path, "to", path)
            if h.path == path and not self.config["OVERWRITE_ALLOWED"]:
                print("Will not overwrite", h.path)
                return
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as file:
                file.write(h.content)
                
    ########## PROCESSING ##########
    
    def ProcessAll(self):
        print("GO")
        self.LoadHtmlFiles()
        self.LoadTemplates()
        self.FindTemplateDependencies()
        self.FindHtmlDependencies()
        self.TopologicalSort()
        self.FillAllFiles()
        self.CopyInputDirectory()
        self.OutputProcessedFiles()
        self.firstPass = True
        
    def ProcessAfterChange(self, fileChanged):
        if not self.firstPass:
            self.ProcessAll()
            return
        
        fileChanged = os.path.normpath(fileChanged)
        
        if fileChanged in [x.path for x in self.htmlFiles]:
            self.ProcessAll()
            return
        
        if fileChanged in [x.path for x in self.templates]:
            self.ProcessAll()
            return
        
        self.CopyFile(fileChanged)
        
