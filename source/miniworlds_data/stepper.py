from __future__ import annotations

from typing import Callable, Generator, List, Optional, Tuple


# A step is a (name, payload) tuple the algorithm yields to mark a visible state.
# Example: ("compare", (i, j)) or ("swap", (i, j)) or ("mark_sorted", i).
Step = Tuple[str, object]


class Stepper:
    """Drives a generator-based algorithm one visible step per frame.

    Classical algorithms written as loops run entirely within a single frame,
    so their intermediate states are never visible. ``Stepper`` solves this by
    letting the algorithm be written as a *generator* that yields once per
    step; the stepper advances it frame by frame (or on demand).

    Each yielded step is a ``(name, payload)`` tuple (see :data:`Step`). The
    stepper records every step so it can replay them forward and backward. For
    backward stepping (``prev_step``, ``reset``, ``goto``) you must pass an
    ``on_reset`` callback that restores the visualization to its initial
    state, since algorithm steps like "swap" are not idempotent.

    Example:
        ::

            from miniworlds_data import ListWorld, Stepper

            world = ListWorld([5, 2, 4, 1, 3])

            def bubble_sort(data):
                n = len(data.values)
                for i in range(n):
                    for j in range(n - i - 1):
                        yield "compare", (j, j + 1)
                        if data.values[j] > data.values[j + 1]:
                            yield "swap", (j, j + 1)

            stepper = Stepper(bubble_sort(world), world, on_step=apply_step)
            stepper.run()  # advances one step per frame automatically
    """

    def __init__(
        self,
        algorithm: Generator[Step, None, None],
        world=None,
        *,
        on_step: Optional[Callable[[Step], None]] = None,
        on_reset: Optional[Callable[[], None]] = None,
        frames_per_step: int = 1,
    ):
        self._algorithm: Optional[Generator[Step, None, None]] = algorithm
        self.world = world
        self._on_step = on_step
        self._on_reset = on_reset
        self._frames_per_step = max(1, int(frames_per_step))
        self._history: List[Step] = []
        self._index: int = -1  # index of the most recently applied step
        self._frame_counter: int = 0
        self._finished: bool = False
        self._registered_worlds = set()

    # -- state -----------------------------------------------------------

    @property
    def steps(self) -> List[Step]:
        """All steps recorded so far, in execution order."""
        return list(self._history)

    @property
    def step_index(self) -> int:
        """Index of the currently applied step (-1 before the first step)."""
        return self._index

    @property
    def finished(self) -> bool:
        """``True`` once the generator has been exhausted."""
        return self._finished

    @property
    def auto_advance(self) -> bool:
        """Whether the stepper advances automatically each frame."""
        return bool(self._registered_worlds)

    # -- single-step control --------------------------------------------

    def next_step(self) -> Optional[Step]:
        """Advance the algorithm by exactly one step and apply it.

        Returns the applied step, or ``None`` at the end of the history
        once the generator has been exhausted.
        """
        # We already have this step in history (e.g. after stepping back).
        next_index = self._index + 1
        if next_index < len(self._history):
            step = self._history[next_index]
        else:
            step = self._pull_next_step()
            if step is None:
                return None

        self._index = next_index
        self._apply(step)
        return step

    def prev_step(self) -> Optional[Step]:
        """Undo the most recently applied step and move backward.

        Returns the step that was undone, or ``None`` at the beginning.

        Raises ``RuntimeError`` if a rewind is needed and no ``on_reset``
        callback was provided.
        """
        if self._index < 0:
            return None
        undone = self._history[self._index]
        self._rewind(self._index - 1)
        return undone

    def reset(self) -> None:
        """Rewind to the beginning and apply no steps.

        Raises ``RuntimeError`` if no ``on_reset`` callback was provided.
        """
        self._rewind(-1)

    def goto(self, index: int) -> None:
        """Move to an absolute step index.

        A negative index rewinds to the start; an index past the end advances
        as far as the generator allows. Backward jumps require ``on_reset``.
        """
        target = max(-1, index)
        if target < self._index:
            self._rewind(target)
            return
        while self._index < target:
            if self.next_step() is None:
                break

    # -- automatic frame-based driving ---------------------------------

    def run(self, world=None) -> None:
        """Register an ``act`` hook on the world that advances one step per frame.

        Args:
            world: World to register on. Defaults to the world passed at
                construction time.
        """
        world = self.world if world is None else world
        if world is None:
            raise ValueError("Stepper.run() needs a world to register the act hook")
        if world in self._registered_worlds:
            return

        @world.register
        def act(_self):
            self.on_frame()

        self._registered_worlds.add(world)

    def on_frame(self) -> Optional[Step]:
        """Advance one step every ``frames_per_step`` frames.

        Call this manually from your own ``act`` hook if you do not use
        :meth:`run`.
        """
        self._frame_counter += 1
        if self._frame_counter < self._frames_per_step:
            return None
        self._frame_counter = 0
        return self.next_step()

    # -- internal --------------------------------------------------------

    def _pull_next_step(self) -> Optional[Step]:
        if self._algorithm is None:
            return None
        try:
            step = next(self._algorithm)
        except StopIteration:
            self._finished = True
            self._algorithm = None
            return None
        self._history.append(step)
        return step

    def _apply(self, step: Step) -> None:
        if self._on_step is not None:
            self._on_step(step)

    def _rewind(self, index: int) -> None:
        if self._on_reset is None:
            raise RuntimeError("Rewinding a Stepper requires an on_reset callback")
        self._on_reset()
        self._index = -1
        self._frame_counter = 0
        for _ in range(index + 1):
            self.next_step()
