"""BFS: breadth-first search from start to target on a graph.

The frontier is advanced one node per act-step so the wavefront is visible.
"""

from collections import deque

from miniworlds_data import GraphWorld

world = GraphWorld(width=500, height=400)
world.fps = 2

a = world.add_node("A", "A", (80, 80))
b = world.add_node("B", "B", (250, 60))
c = world.add_node("C", "C", (420, 100))
d = world.add_node("D", "D", (150, 250))
e = world.add_node("E", "E", (350, 280))

world.connect(a, b)
world.connect(b, c)
world.connect(a, d)
world.connect(d, e)
world.connect(c, e)
world.connect(b, d)

world.set_start(a)
world.set_target(e)

frontier = deque([a])
parent = {a: None}
current = None
done = False


@world.register
def act(self):
    global current, done
    if done:
        return
    if current is not None:
        world.highlight(current, "start" if current is a else "visited")
    if not frontier:
        done = True
        return

    current = frontier.popleft()
    if current is e:
        path = []
        node = current
        while node is not None:
            path.append(node)
            node = parent[node]
        world.path_edges(reversed(path))
        for node in path[1:-1]:
            world.highlight(node, "path")
        for node in frontier:
            world.highlight(node, "default")
        frontier.clear()
        world.highlight(current, "target")
        done = True
        return

    world.highlight(current, "current")
    for neighbor in world.neighbors(current):
        if neighbor not in parent:
            parent[neighbor] = current
            frontier.append(neighbor)
            if neighbor is not e:
                world.highlight(neighbor, "frontier")
            world.highlight_edge(current, neighbor, "visited")


world.run()
