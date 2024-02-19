# provides a class to filter files (and directories) using .gitignore-like syntax

import os
import re
from fnmatch import fnmatch



class FileFilter:
    def __init__(self, ignoreList=None):
        self.ignorePatterns = []
        if ignoreList is not None:
            self.ignorePatterns = ignoreList

    def IgnoreFunc(self, path):
        return any(fnmatch(path, pattern) for pattern in self.ignorePatterns)


# test
ignoresList = ["*.git/*", "*output/*", "*.gitignore"]
testPaths = [
    "test.tml",
    "test.html",
    "test.git",
    "output/help.txt",
    "../output/help.txt",
    ".gitignore",
    "test.txt",
    "../../.git/file.asdf",
]

ff = FileFilter(ignoresList)
print(ignoresList)
print("\n".join([str((p, ff.IsIgnored(p))) for p in testPaths]))


igpats = [".git", "__pycache__", "*.gitignore", "*.txt"]

def igfn(pth, names):
    print(path.normpath(pth), names)
    print("---------------")
    ignored = []
    for name in names:
        if any(fnmatch(name, pattern) for pattern in igpats):
            ignored.append(name)
    print(ignored)
    print("---------------///")
    return ignored
shutil.copytree("../web-template", "move", dirs_exist_ok=True, ignore=igfn)