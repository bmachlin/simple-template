# class that is given a list of HTML and TML file paths
# then generates a dependency graph
# It checks for circular dependencies
# It can say which files need to be recompiled when a file is changed

class Dependencies:
    def __init__(self, dependencies):
        self.dependencies = dependencies
        self.dependencyGraph = {}
    
    def generateGraph(self):
        for dependency in self.dependencies:
            self.dependencyGraph[dependency] = self.findDependencies(dependency)
    
    def findDependencies(self, dependency):
        dependencies = set()
        self.findDependenciesHelper(dependency, dependencies)
        return dependencies
    
    def checkCircularDependencies(self):
        for dependency in self.dependencies:
            if self.checkCircularDependenciesHelper(dependency, dependency):
                return True
        return False
    
    def checkCircularDependenciesHelper(self, dependency, start):
        for d in self.dependencyGraph[dependency]:
            if d == start:
                return True
            if self.checkCircularDependenciesHelper(d, start):
                return True
        return False
    