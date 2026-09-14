"""Bubble Sort: visualize one comparison and swap per act-step.

The algorithm is driven frame-by-frame so every step is visible, unlike a
plain for-loop which would run inside a single frame.
"""

from miniworlds import Number
from miniworlds_data import ListWorld

world = ListWorld([5, 2, 9, 1, 6, 3], cell_width=60, bar_height=220)
world.fps = 4

i = Number((10, 10), 0)
i.font_size = 16
j = Number((60, 10), 0)
j.font_size = 16
comparisons = Number((world.width - 80, 10), 0)
comparisons.font_size = 16

state = {"i": 0, "j": 0, "swapped": False, "done": False}


@world.register
def act(self):
    global state
    if state["done"]:
        return

    world.reset_all()
    i.set_number(state["i"])
    j.set_number(state["j"])

    if state["i"] >= world.length - 1:
        for k in range(world.length):
            world.mark_sorted(k)
        state["done"] = True
        return

    a, b = state["j"], state["j"] + 1
    comparisons.add(1)
    if world.compare(a, b):
        world.swap(a, b)
        state["swapped"] = True

    state["j"] += 1
    if state["j"] >= world.length - 1 - state["i"]:
        world.mark_sorted(world.length - 1 - state["i"])
        state["i"] += 1
        state["j"] = 0
        if not state["swapped"]:
            state["done"] = True
            for k in range(world.length):
                world.mark_sorted(k)
        state["swapped"] = False


world.run()
