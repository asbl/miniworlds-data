# miniworlds_data

`miniworlds_data` is an extension library for miniworlds. It provides pixel
worlds that visualize classic data structures so that algorithms (search,
sorting, traversal, pathfinding) can be shown step by step.

The library builds everything from miniworlds worlds and actors. It does not
load pygame sprites or expose pygame primitives.

The package is intentionally kept separate from the miniworlds core package so
it can later live in its own repository and be published on PyPI.

## Worlds

| World        | Visualizes           | Typical algorithms                         |
|--------------|----------------------|--------------------------------------------|
| `ListWorld`  | array of bars        | linear/binary search, bubble/selection sort |
| `StackWorld` | LIFO stack           | recursion / call-stack, DFS, undo          |
| `QueueWorld` | FIFO queue           | BFS frontier                               |
| `TreeWorld`  | binary tree          | traversals (pre/in/post-order), BST search |
| `GraphWorld` | graph with edges     | BFS, DFS, shortest path                    |

Each world uses the same standardized color language for highlight states
(`default`, `compare`, `swap`, `sorted`, `pivot`, `visited`, `current`,
`frontier`, `start`, `target`, `path`).

## Stepper

Algorithms written as plain loops run inside a single frame, so intermediate
states are never visible. `Stepper` solves this: the algorithm is written as a
*generator* that `yield`s once per step, and the stepper advances it one step
per frame (or on demand).

```python
from miniworlds_data import ListWorld, Stepper

initial = [5, 2, 4, 1, 3]
world = ListWorld(initial)


def apply_step(step):
    name, (i, j) = step
    world.reset_all()
    if name == "compare":
        world.compare(i, j)
    elif name == "swap":
        world.swap(i, j)


def bubble_sort(data):
    n = data.length
    for i in range(n):
        for j in range(n - i - 1):
            yield "compare", (j, j + 1)
            if data.values[j] > data.values[j + 1]:
                yield "swap", (j, j + 1)


stepper = Stepper(bubble_sort(world), world, on_step=apply_step)
stepper.run()  # advances one step per frame
world.run()
```

`Stepper` also supports single stepping (`next_step`), going back
(`prev_step`, requires an `on_reset` callback), `reset`, and `goto`.

## Example: sorting

```python
from miniworlds_data import ListWorld

world = ListWorld([5, 2, 4, 1, 3])
world.compare(0, 1)
world.swap(0, 1)
world.mark_sorted(0)
world.run()
```

## Example: graph pathfinding

```python
from miniworlds_data import GraphWorld

world = GraphWorld()
a = world.add_node("A", "A", (100, 100))
b = world.add_node("B", "B", (300, 100))
c = world.add_node("C", "C", (200, 250))
world.connect(a, b)
world.connect(a, c)
world.connect(b, c)
world.set_start(a)
world.set_target(c)
world.run()
```
