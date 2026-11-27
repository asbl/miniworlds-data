"""Bubble Sort with the Stepper: the algorithm reads like a textbook loop.

The Stepper drives the generator one ``yield`` per frame, so every comparison
and swap is visible. Compare this to ``01_bubble_sort.py``, which had to encode
the loop indices in an explicit state machine.
"""

from miniworlds_data import ListWorld, Stepper

initial = [5, 2, 9, 1, 6, 3]
world = ListWorld(initial, cell_width=60, bar_height=220)
world.fps = 6
highlighted = ()


def apply_step(step):
    global highlighted
    name, payload = step
    for index in highlighted:
        world.reset_color(index)
    highlighted = ()
    if name == "compare":
        world.compare(*payload)
        highlighted = payload
    elif name == "swap":
        world.swap(*payload)
        highlighted = payload
    elif name == "sorted":
        for i in payload:
            world.mark_sorted(i)


def reset():
    global highlighted
    highlighted = ()
    for i, value in enumerate(initial):
        world.set_value(i, value)
    world.reset_all()


def bubble_sort(data):
    for end in range(data.length - 1, 0, -1):
        swapped = False
        for j in range(end):
            yield "compare", (j, j + 1)
            values = data.values
            if values[j] > values[j + 1]:
                yield "swap", (j, j + 1)
                swapped = True
        if not swapped:
            yield "sorted", tuple(range(end + 1))
            return
        yield "sorted", (end,)
    yield "sorted", (0,)


stepper = Stepper(
    bubble_sort(world),
    world,
    on_step=apply_step,
    on_reset=reset,
)
stepper.run()
world.run()
