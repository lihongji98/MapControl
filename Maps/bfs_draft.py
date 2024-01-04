from collections import deque
"""
        1
    2       3
  4  5     6  7
8
"""


def bfs(graph, start):
    visited_nodes = set()
    to_visit_nodes = deque([(start, 0)])
    max_depth = 2

    while to_visit_nodes:
        search_node, depth = to_visit_nodes.popleft()
        if search_node not in visited_nodes and depth < max_depth:
            visited_nodes.add(search_node)
            print(search_node, end=' ')
            for neighbor in graph.get(search_node, []):
                if neighbor not in visited_nodes:
                    to_visit_nodes.append((neighbor, depth+1))


Graph = {1: [2, 3],
         2: [4, 5],
         3: [6, 7],
         4: [8]}

bfs(Graph, 1)
