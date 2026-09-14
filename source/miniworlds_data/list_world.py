from __future__ import annotations

from typing import List, Optional, Tuple

from miniworlds import Number, Rectangle, Text, World


Color = Tuple[int, int, int] | Tuple[int, int, int, int]


# Standardized algorithm-visualization color language.
DEFAULT_COLOR: Color = (130, 170, 200, 255)        # idle / unsorted
COMPARE_COLOR: Color = (245, 200, 60, 255)         # currently being compared
SWAP_COLOR: Color = (220, 60, 60, 255)             # about to be swapped
SORTED_COLOR: Color = (90, 190, 110, 255)          # final position reached
PIVOT_COLOR: Color = (160, 110, 220, 255)          # pivot / current key
MARK_COLOR: Color = (60, 140, 210, 255)            # arbitrary marker (min/max index)
TEXT_COLOR: Color = (20, 20, 20, 255)


class _ListCell(Rectangle):
    """A single visual cell (bar + value label) of a :class:`ListWorld`."""

    def __init__(
        self,
        value: int | float,
        *,
        world: "ListWorld",
        index: int,
        color: Color,
        width: float,
        height: float,
        label_height: float,
    ):
        super().__init__((0, 0), width, height, world=world)
        self.origin = "topleft"
        self.fill_color = color
        self.border = 1
        self.border_color = (255, 255, 255, 255)
        self.is_static = True
        self.value: int | float = value
        self.index: int = index
        self._state: str = "default"
        self.label_height = label_height
        self._label = Text((0, 0), str(value), world=world)
        self._label.origin = "topleft"
        self._label.color = TEXT_COLOR
        self._label.font_size = max(10, int(label_height * 0.6))
        self._label.is_static = True

    @property
    def state(self) -> str:
        return self._state

    def set_state(self, state: str, color: Optional[Color] = None) -> None:
        self._state = state
        self.fill_color = color if color is not None else _STATE_COLORS[state]

    def set_value(self, value: int | float) -> None:
        self.value = value
        self._label.set_text(str(value))

    def move_to_slot(self, x: float, bar_y: float) -> None:
        self.topleft = (x, bar_y)
        label_y = bar_y + self.height + 2
        self._label.topleft = (x, label_y)

    def remove_label(self) -> None:
        if self._label.world is not None:
            self._label.remove()


_STATE_COLORS = {
    "default": DEFAULT_COLOR,
    "compare": COMPARE_COLOR,
    "swap": SWAP_COLOR,
    "sorted": SORTED_COLOR,
    "pivot": PIVOT_COLOR,
    "mark": MARK_COLOR,
}


class ListWorld(World):
    """Pixel world that visualizes a list of values as an array of bars.

    The world exposes high-level operations such as ``highlight()``,
    ``compare()``, and ``swap()`` that algorithms use to make single steps
    visible. The named states are ``default``, ``compare``, ``swap``,
    ``sorted``, ``pivot``, and ``mark``.

    Example:
        ``ListWorld([5, 2, 4, 1, 3])`` creates a bar visualization. Calling
        ``compare(0, 1)``, ``swap(0, 1)``, and ``mark_sorted(0)`` updates the
        visible state for a sorting algorithm.
    """

    def __init__(
        self,
        values: List[int | float] | None = None,
        *,
        cell_width: int = 50,
        bar_height: int = 200,
        label_height: int = 30,
        margin: int = 10,
        background: Color = (245, 245, 245, 255),
    ):
        values = list(values) if values is not None else []
        if not values:
            raise ValueError("ListWorld requires at least one value")
        if any(not isinstance(v, (int, float)) for v in values):
            raise TypeError("ListWorld values must be int or float")

        self._max_value: int | float = max(values)
        self._min_value: int | float = min(min(values), 0)
        self._cell_width = cell_width
        self._bar_height = bar_height
        self._label_height = label_height
        self._margin = margin
        self._cells: List[_ListCell] = []

        width = len(values) * cell_width + margin * 2
        height = bar_height + label_height + margin * 2 + label_height
        super().__init__(width, height)
        self.background.fill_color = background

        self._value_range = max(self._max_value - self._min_value, 1)
        for index, value in enumerate(values):
            self._cells.append(self._build_cell(value, index))
        self._relayout()

    def _build_cell(self, value: int | float, index: int) -> _ListCell:
        return _ListCell(
            value,
            world=self,
            index=index,
            color=DEFAULT_COLOR,
            width=self._cell_width,
            height=self._bar_height,
            label_height=self._label_height,
        )

    def _bar_height_for_value(self, value: int | float) -> float:
        normalized = (value - self._min_value) / self._value_range
        return max(self._bar_height * 0.05, self._bar_height * normalized)

    def _relayout(self) -> None:
        base_y = self._margin + self._bar_height
        for index, cell in enumerate(self._cells):
            x = self._margin + index * self._cell_width
            bar_y = base_y - self._bar_height_for_value(cell.value)
            cell.height = self._bar_height_for_value(cell.value)
            cell.move_to_slot(x, bar_y)

    # -- read access -----------------------------------------------------

    @property
    def values(self) -> List[int | float]:
        """Current values, read left-to-right."""
        return [cell.value for cell in self._cells]

    @property
    def length(self) -> int:
        return len(self._cells)

    def is_sorted(self) -> bool:
        """Return ``True`` when the values are non-decreasing."""
        values = self.values
        return all(values[i] <= values[i + 1] for i in range(len(values) - 1))

    # -- high-level algorithm operations --------------------------------

    def set_color(self, index: int, state: str, color: Optional[Color] = None) -> None:
        """Color a cell with a named state or an explicit color.

        Args:
            index: Cell index.
            state: One of ``default``, ``compare``, ``swap``, ``sorted``,
                ``pivot``, ``mark``.
            color: Optional explicit color overriding the state's default color.
        """
        self._cells[self._validate_index(index)].set_state(state, color)

    def highlight(self, index: int, state: str = "compare") -> None:
        """Color a cell with one of the named states.

        Args:
            index: Cell index.
            state: Named state (see class docstring).
        """
        self.set_color(index, state)

    def mark_sorted(self, index: int) -> None:
        """Mark a cell as having reached its final (sorted) position."""
        self.set_color(index, "sorted")

    def reset_color(self, index: int) -> None:
        """Reset a cell back to the default (unsorted) color."""
        self.set_color(index, "default")

    def reset_all(self) -> None:
        """Reset every cell back to the default color."""
        for index in range(self.length):
            self.reset_color(index)

    def compare(self, i: int, j: int) -> bool:
        """Highlight cells ``i`` and ``j`` and return ``values[i] > values[j]``.

        This is the canonical "one comparison" step for sorting/search tasks.
        """
        self._validate_index(i)
        self._validate_index(j)
        self.set_color(i, "compare")
        self.set_color(j, "compare")
        return self.values[i] > self.values[j]

    def swap(self, i: int, j: int) -> None:
        """Swap the values (and bar heights) of cells ``i`` and ``j``.

        Both cells are colored with the ``swap`` state during the operation.
        """
        self._validate_index(i)
        self._validate_index(j)
        cell_i, cell_j = self._cells[i], self._cells[j]
        cell_i.set_state("swap")
        cell_j.set_state("swap")
        cell_i.value, cell_j.value = cell_j.value, cell_i.value
        cell_i.set_value(cell_i.value)
        cell_j.set_value(cell_j.value)
        self._relayout()

    def set_value(self, index: int, value: int | float) -> None:
        """Set the value of a cell and relayout all bars."""
        if not isinstance(value, (int, float)):
            raise TypeError("value must be int or float")
        self._cells[self._validate_index(index)].set_value(value)
        if value > self._max_value:
            self._max_value = value
        if value < self._min_value:
            self._min_value = value
        self._value_range = max(self._max_value - self._min_value, 1)
        self._relayout()

    def _validate_index(self, index: int) -> int:
        if not isinstance(index, int):
            raise TypeError(f"index must be int, got {type(index).__name__}")
        if index < 0 or index >= self.length:
            raise IndexError(f"ListWorld index {index} out of range (0..{self.length - 1})")
        return index
