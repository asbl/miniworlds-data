"""Bubble Sort with the Stepper: the algorithm reads like a textbook loop.

The Stepper drives the generator one ``yield`` per frame, so every comparison
and swap is visible. Compare this to ``01_bubble_sort.py``, which had to encode
the loop indices in an explicit state machine.
"""

from miniworlds_data import ListWorld, Stepper

initial = [5, 2, 9, 1, 6, 3]
world = ListWorld(initial, cell_width=60, bar_height=220)
world.fps = 6


def apply_step(step):
    name, payload = step
    world.reset_all()
    if name == "compare":
        world.compare(*payload)
    elif name == "swap":
        world.swap(*payload)
    elif name == "sorted":
        for i in payload:
            world.mark_sorted(i)


def reset():
    for i, value in enumerate(initial):
        world.set_value(i, value)
    world.reset_all()


def bubble_sort(data):
    n = data.length
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            yield "compare", (j, j + 1)
            if data.values[j] > data.values[j + 1]:
                yield "swap", (j, j + 1)
                swapped = True
        yield "sorted", tuple(range(n - i - 1, n))
        if not swapped:
            yield "sorted", tuple(range(0, n - i - 1))
            return


stepper = Stepper(
    bubble_sort(world),
    world,
    on_step=apply_step,
    on_reset=reset,
)
stepper.run()
world.run()
