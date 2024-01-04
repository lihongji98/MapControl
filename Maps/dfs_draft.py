from collections import deque

"""
        1
    2       3
  4  5     6  7
8
"""


def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    stack = deque([(start, 1)])
    max_depth = 3

    while stack:
        node, depth = stack.pop()
        if node not in visited:
            print(node, end=' ')
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited and depth < max_depth:
                    stack.append((neighbor, depth + 1))


def dfs_recursive(graph, start, visited=None, max_depth=3, depth=1):
    if visited is None:
        visited = set()

    visited.add(start)

    print(start, end=' ')

    for neighbor in graph.get(start, []):
        if neighbor not in visited and depth < max_depth:
            visited.add(neighbor)
            dfs_recursive(graph, neighbor, visited, max_depth, depth+1)


Graph = {1: [2, 3],
         2: [4, 5],
         3: [6, 7],
         4: [8]}
dfs(Graph, 1)
