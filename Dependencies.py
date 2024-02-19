# return a dependency graph in the form of:
# graph[a] = [b,c] where a depends on b and c
def BuildGraph(htmlFiles, templates):
    dependsOn = {}
    for h in htmlFiles:
        dependsOn[h.path] = h.dependencies
    for t in templates:
        dependsOn[t.id] = t.dependencies
    return dependsOn
    

# https://www.geeksforgeeks.org/topological-sorting-indegree-based-solution/
# return a topological sort of the graph, from least dependencies to most
# i.e. process the first element before the second, etc.
def TopologicalSort(htmlFiles, templates):
    graph = BuildGraph(htmlFiles, templates)
    
    # compute in-degrees of all vertices.
    indegree = {v: 0 for v in graph.keys()}
    for i in graph:
        for j in graph[i]:
            indegree[j] += 1

    # enqueue all vertices with in-degree 0
    queue = [v for v in graph.keys() if indegree[v] == 0]
    visitedVertices = []
    topOrder = []

    while queue:
        # dequeue and add to topological order
        v = queue.pop(0)
        topOrder.insert(0,v)

        # Iterate neighboring vertices of dequeued vertex v and decrease their in-degrees by 1
        for d in graph[v]:
            indegree[d] -= 1
            # If in-degree becomes zero, add it to queue
            if indegree[d] == 0:
                queue.append(d)

        visitedVertices.append(v)

    if len(visitedVertices) != len(graph):
        print("There exists a cycle in the graph", len(visitedVertices), len(graph))
        return None
    else:
        return topOrder
    