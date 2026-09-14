from __future__ import annotations

from typing import List, Optional, Tuple

from miniworlds import Rectangle, Text, World


Color = Tuple[int, int, int] | Tuple[int, int, int, int]


DEFAULT_COLOR: Color = (130, 170, 200, 255)
FRONT_COLOR: Color = (220, 60, 60, 255)
BACK_COLOR: Color = (160, 110, 220, 255)
TEXT_COLOR: Color = (20, 20, 20, 255)
EMPTY_COLOR: Color = (120, 120, 120, 255)


class _QueueBox(Rectangle):
    """A single element box inside a :class:`QueueWorld`."""

    def __init__(
        self,
        value: object,
        *,
        world: "QueueWorld",
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


class QueueWorld(World):
    """Pixel world that visualizes a FIFO queue growing left-to-right.

    Elements are enqueued at the back and dequeued at the front. The front
    box is highlighted in red, the back box in purple.

    Example:
        ::

            from miniworlds_data import QueueWorld

            world = QueueWorld()
            world.enqueue(3)
            world.enqueue(7)
            world.enqueue(2)
            print(world.front())   # 3
            print(world.dequeue()) # 3
            world.run()
    """

    def __init__(
        self,
        *,
        capacity: int = 8,
        box_width: int = 80,
        box_height: int = 50,
        margin: int = 10,
        background: Color = (245, 245, 245, 255),
    ):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._box_width = box_width
        self._box_height = box_height
        self._margin = margin
        self._boxes: List[_QueueBox] = []

        width = capacity * box_width + margin * 2
        height = box_height + margin * 2 + 20
        super().__init__(width, height)
        self.background.fill_color = background
        self._front_label = Text((margin, margin + box_height + 2), "front", world=self)
        self._front_label.color = EMPTY_COLOR
        self._front_label.font_size = 12
        self._front_label.is_static = True


    def __len__(self) -> int:
        return len(self._boxes)

    def is_empty(self) -> bool:
        return not self._boxes

    def is_full(self) -> bool:
        return len(self._boxes) >= self._capacity

    def front(self) -> object:
        """Return the front element without removing it.

        Raises:
            IndexError: when the queue is empty.
        """
        if self.is_empty():
            raise IndexError("front of empty queue")
        return self._boxes[0].value

    def back(self) -> object:
        """Return the back element without removing it.

        Raises:
            IndexError: when the queue is empty.
        """
        if self.is_empty():
            raise IndexError("back of empty queue")
        return self._boxes[-1].value

    def values(self) -> List[object]:
        """Return the current elements, front-to-back order."""
        return [box.value for box in self._boxes]

    def enqueue(self, value: object) -> None:
        """Add ``value`` to the back of the queue.

        Raises:
            OverflowError: when the queue is already at capacity.
        """
        if self.is_full():
            raise OverflowError(f"queue overflow (capacity {self._capacity})")
        box = _QueueBox(
            value,
            world=self,
            color=DEFAULT_COLOR,
            width=self._box_width,
            height=self._box_height,
        )
        self._boxes.append(box)
        self._relayout()

    def dequeue(self) -> object:
        """Remove and return the front element.

        Raises:
            IndexError: when the queue is empty.
        """
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        box = self._boxes.pop(0)
        box.remove_label()
        box.remove()
        self._relayout()
        return box.value

    def clear_elements(self) -> None:
        """Remove every element from the queue."""
        for box in self._boxes:
            box.remove_label()
            box.remove()
        self._boxes.clear()
        self._relayout()

    def _relayout(self) -> None:
        y = self._margin
        for index, box in enumerate(self._boxes):
            x = self._margin + index * self._box_width
            box.move_to_slot(x, y)
            if index == 0:
                box.fill_color = FRONT_COLOR
            elif index == len(self._boxes) - 1:
                box.fill_color = BACK_COLOR
            else:
                box.fill_color = DEFAULT_COLOR
        self._front_label.text = "front" if self._boxes else "empty"
