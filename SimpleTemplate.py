import os, json, time, shutil, bs4
from fnmatch import fnmatch
from bs4 import BeautifulSoup
from FileObject import FileObject
from Template import Template
from TemplateLoader import TemplateLoader
import Dependencies


class SimpleTemplate:
    def __init__(self, config=None, configPath=None):
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
            "OUTPUT_DIR": "output",
            "TEMPLATE_DIR": "templates",
            "INPUT_DIR": ".",
            "EXCLUDE_ALL": [],
            "EXCLUDED_HTML": [],
            "EXCLUDED_TEMPLATE": [],
            "EXCLUDED_COPY": [],
        }

        # apply zero, one, or both config options
        if configPath is not None:
            self.LoadConfigFromPath(configPath)
        if config is not None:
            self.LoadConfig(config)

    ########## CONFIG ##########

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
        ignorePatters = self.config["EXCLUDE_ALL"] + self.config["EXCLUDED_HTML"]
        for root, dirs, files in os.walk(self.config["INPUT_DIR"]):
            for file in files:
                if file.endswith(".html") and not any(fnmatch(os.path.join(root, file), pattern) for pattern in ignorePatters):
                    # print(os.path.join(root, file))
                    obj = FileObject()
                    obj.path = os.path.join(root, file)
                    fps.append(obj)
        return fps

    def GetTemplateFilePaths(self):
        fps = []
        ignorePatters = self.config["EXCLUDE_ALL"] + self.config["EXCLUDED_TEMPLATE"]
        for root, dirs, files in os.walk(self.config["TEMPLATE_DIR"]):
            for file in files:
                if file.endswith(".tml") and not any(fnmatch(os.path.join(root, file), pattern) for pattern in ignorePatters):
                    obj = Template()
                    obj.path = os.path.join(root, file)
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
                content = content.replace(
                    self.config["TEMPLATE_VAR_START"]
                    + v
                    + self.config["TEMPLATE_VAR_END"],
                    value,
                )

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
        # print("Copying files from", self.inputRoot, "to", self.outputRoot)
        ignorePatterns = self.config["EXCLUDE_ALL"] + self.config["EXCLUDED_COPY"]
        def ignoreFn(path, names):
            ignored = []
            for name in names:
                # print(os.path.join(os.path.normpath(path), name))
                for pattern in ignorePatterns:
                    fp = os.path.join(os.path.normpath(path), name)
                    if fnmatch(fp, pattern):
                        print("Not copying", fp, "because of", pattern)
                        ignored.append(name)
            return ignored
        
        shutil.copytree(self.config["INPUT_DIR"], self.config["OUTPUT_DIR"], dirs_exist_ok=True, ignore=ignoreFn)

    def OutputProcessedFiles(self):
        # print("Outputting processed files to", self.outputRoot)
        # os.umask(0o077) # do I need this?
        for h in self.htmlFiles:
            # set path to replace input directory with output directory
            path = h.path.replace(self.config["INPUT_DIR"], self.config["OUTPUT_DIR"])
            # print(path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as file:
                file.write(h.content)
