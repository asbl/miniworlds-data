from __future__ import annotations

from typing import List, Optional, Tuple

from miniworlds import Rectangle, Text, World


Color = Tuple[int, int, int] | Tuple[int, int, int, int]


DEFAULT_COLOR: Color = (130, 170, 200, 255)
TOP_COLOR: Color = (220, 60, 60, 255)
TEXT_COLOR: Color = (20, 20, 20, 255)
EMPTY_COLOR: Color = (120, 120, 120, 255)


class _StackBox(Rectangle):
    """A single element box inside a :class:`StackWorld`."""

    def __init__(
        self,
        value: object,
        *,
        world: "StackWorld",
        color: Color,
        width: float,
        height: float,
    ):
        super().__init__((0, 0), width, height, world=world)
        self.origin = "topleft"
        self.fill_color = color
        self.border = 1
        self.border_color = (255, 255, 255, 255)
        self.is_static = True
        self.value = value
        self._label = Text((0, 0), str(value), world=world)
        self._label.origin = "topleft"
        self._label.color = TEXT_COLOR
        self._label.font_size = max(12, int(height * 0.5))
        self._label.is_static = True

    def move_to_slot(self, x: float, y: float) -> None:
        self.topleft = (x, y)
        label_x = x + self.width / 2 - self._label.get_text_width() / 2
        label_y = y + self.height / 2 - self._label.font_size / 2
        self._label.topleft = (label_x, label_y)

    def remove_label(self) -> None:
        if self._label.world is not None:
            self._label.remove()


class StackWorld(World):
    """Pixel world that visualizes a LIFO stack growing upward.

    Elements are pushed onto the top and popped from the top. The topmost box
    is highlighted in red.

    Example:
        ::

            from miniworlds_data import StackWorld

            world = StackWorld()
            world.push(3)
            world.push(7)
            world.push(2)
            print(world.peek())   # 2
            print(world.pop())    # 2
            world.run()
    """

    def __init__(
        self,
        *,
        capacity: int = 8,
        box_width: int = 120,
        box_height: int = 40,
        margin: int = 10,
        background: Color = (245, 245, 245, 255),
    ):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._box_width = box_width
        self._box_height = box_height
        self._margin = margin
        self._boxes: List[_StackBox] = []

        width = box_width + margin * 2
        height = capacity * box_height + margin * 2
        super().__init__(width, height)
        self.background.fill_color = background
        self._top_label = Text((margin, 2), "top", world=self)
        self._top_label.color = EMPTY_COLOR
        self._top_label.font_size = 12
        self._top_label.is_static = True


    def __len__(self) -> int:
        return len(self._boxes)

    def is_empty(self) -> bool:
        return not self._boxes

    def is_full(self) -> bool:
        return len(self._boxes) >= self._capacity

    def peek(self) -> object:
        """Return the top element without removing it.

        Raises:
            IndexError: when the stack is empty.
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._boxes[-1].value

    def values(self) -> List[object]:
        """Return the current elements, bottom-to-top order."""
        return [box.value for box in self._boxes]

    def push(self, value: object) -> None:
        """Push ``value`` onto the top of the stack.

        Raises:
            OverflowError: when the stack is already at capacity.
        """
        if self.is_full():
            raise OverflowError(f"stack overflow (capacity {self._capacity})")
        box = _StackBox(
            value,
            world=self,
            color=DEFAULT_COLOR,
            width=self._box_width,
            height=self._box_height,
        )
        self._boxes.append(box)
        self._relayout()

    def pop(self) -> object:
        """Remove and return the top element.

        Raises:
            IndexError: when the stack is empty.
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        box = self._boxes.pop()
        box.remove_label()
        box.remove()
        self._relayout()
        return box.value

    def clear_elements(self) -> None:
        """Remove every element from the stack."""
        for box in self._boxes:
            box.remove_label()
            box.remove()
        self._boxes.clear()
        self._relayout()

    def _relayout(self) -> None:
        x = self._margin
        for index, box in enumerate(self._boxes):
            y = self.height - self._margin - (index + 1) * self._box_height
            box.move_to_slot(x, y)
            box.fill_color = TOP_COLOR if index == len(self._boxes) - 1 else DEFAULT_COLOR
        self._top_label.text = "top" if self._boxes else "empty"
