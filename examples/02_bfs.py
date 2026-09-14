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
visited = {a.name}


@world.register
def act(self):
    if not frontier:
        return
    current = frontier.popleft()
    world.highlight(current, "current")
    if current is e:
        world.highlight(current, "target")
        return
    for neighbor in world.neighbors(current):
        if neighbor.name not in visited:
            visited.add(neighbor.name)
            frontier.append(neighbor)
            world.highlight(neighbor, "frontier")
            world.highlight_edge(current, neighbor, "visited")


world.run()
