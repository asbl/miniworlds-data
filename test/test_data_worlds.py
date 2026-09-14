import pytest

from miniworlds_data import GraphWorld, ListWorld, QueueWorld, StackWorld, Stepper, TreeWorld


pytestmark = pytest.mark.filterwarnings(
    r"ignore:\[world_name\]\.run\(\) was not found:UserWarning"
)


# ---------------------------------------------------------------- ListWorld


class TestListWorld:
    def test_creates_cells_for_each_value(self):
        world = ListWorld([5, 2, 4])
        assert world.values == [5, 2, 4]
        assert world.length == 3

    def test_rejects_empty_values(self):
        with pytest.raises(ValueError):
            ListWorld([])

    def test_rejects_non_numeric_values(self):
        with pytest.raises(TypeError):
            ListWorld([1, "a", 3])

    def test_swap_exchanges_values(self):
        world = ListWorld([5, 2, 4])
        world.swap(0, 2)
        assert world.values == [4, 2, 5]

    def test_compare_returns_greater_than_relation(self):
        world = ListWorld([5, 2, 4])
        assert world.compare(0, 1) is True
        assert world.compare(1, 0) is False

    def test_mark_sorted_sets_sorted_state(self):
        world = ListWorld([5, 2, 4])
        world.mark_sorted(0)
        assert world._cells[0].state == "sorted"

    def test_reset_all_clears_states(self):
        world = ListWorld([5, 2, 4])
        world.compare(0, 1)
        world.reset_all()
        assert all(cell.state == "default" for cell in world._cells)

    def test_is_sorted_detection(self):
        world = ListWorld([1, 2, 3])
        assert world.is_sorted() is True
        world.swap(0, 2)
        assert world.is_sorted() is False

    def test_set_value_updates_values_and_layout(self):
        world = ListWorld([1, 2, 3])
        world.set_value(0, 99)
        assert world.values == [99, 2, 3]
        assert world.is_sorted() is False

    def test_invalid_index_raises(self):
        world = ListWorld([1, 2, 3])
        with pytest.raises(IndexError):
            world.swap(0, 5)

    def test_set_color_with_explicit_color(self):
        world = ListWorld([1, 2, 3])
        world.set_color(0, "default", (10, 20, 30, 255))
        assert world._cells[0].fill_color == (10, 20, 30, 255)


# --------------------------------------------------------------- StackWorld


class TestStackWorld:
    def test_push_and_peek(self):
        world = StackWorld()
        world.push(3)
        world.push(7)
        assert world.peek() == 7
        assert len(world) == 2

    def test_pop_returns_and_removes_top(self):
        world = StackWorld()
        world.push(3)
        world.push(7)
        assert world.pop() == 7
        assert len(world) == 1
        assert world.peek() == 3

    def test_pop_empty_raises(self):
        world = StackWorld()
        with pytest.raises(IndexError):
            world.pop()

    def test_peek_empty_raises(self):
        world = StackWorld()
        with pytest.raises(IndexError):
            world.peek()

    def test_is_empty_and_is_full(self):
        world = StackWorld(capacity=2)
        assert world.is_empty() is True
        world.push(1)
        assert world.is_empty() is False
        world.push(2)
        assert world.is_full() is True

    def test_overflow_raises(self):
        world = StackWorld(capacity=1)
        world.push(1)
        with pytest.raises(OverflowError):
            world.push(2)

    def test_values_in_bottom_to_top_order(self):
        world = StackWorld()
        for v in [1, 2, 3]:
            world.push(v)
        assert world.values() == [1, 2, 3]

    def test_clear_removes_all(self):
        world = StackWorld()
        world.push(1)
        world.push(2)
        world.clear_elements()
        assert world.is_empty() is True
        assert len(world) == 0

    def test_len_protocol(self):
        world = StackWorld()
        world.push(1)
        assert len(world) == 1


# --------------------------------------------------------------- QueueWorld


class TestQueueWorld:
    def test_enqueue_and_front(self):
        world = QueueWorld()
        world.enqueue(3)
        world.enqueue(7)
        assert world.front() == 3
        assert world.back() == 7
        assert len(world) == 2

    def test_dequeue_returns_and_removes_front(self):
        world = QueueWorld()
        world.enqueue(3)
        world.enqueue(7)
        assert world.dequeue() == 3
        assert len(world) == 1
        assert world.front() == 7

    def test_dequeue_empty_raises(self):
        world = QueueWorld()
        with pytest.raises(IndexError):
            world.dequeue()

    def test_front_empty_raises(self):
        world = QueueWorld()
        with pytest.raises(IndexError):
            world.front()

    def test_fifo_order(self):
        world = QueueWorld()
        for v in [1, 2, 3]:
            world.enqueue(v)
        order = [world.dequeue() for _ in range(3)]
        assert order == [1, 2, 3]

    def test_overflow_raises(self):
        world = QueueWorld(capacity=1)
        world.enqueue(1)
        with pytest.raises(OverflowError):
            world.enqueue(2)

    def test_clear_removes_all(self):
        world = QueueWorld()
        world.enqueue(1)
        world.enqueue(2)
        world.clear_elements()
        assert world.is_empty() is True


# ---------------------------------------------------------------- TreeWorld


class TestTreeWorld:
    def test_set_root_creates_root_node(self):
        world = TreeWorld()
        root = world.set_root(5)
        assert root.value == 5
        assert world.root is root
        assert root.state == "root"

    def test_add_left_and_right_children(self):
        world = TreeWorld()
        root = world.set_root(5)
        left = world.add_left(root, 3)
        right = world.add_right(root, 8)
        assert root.left is left
        assert root.right is right
        assert root.left.value == 3
        assert root.right.value == 8

    def test_double_left_child_raises(self):
        world = TreeWorld()
        root = world.set_root(5)
        world.add_left(root, 3)
        with pytest.raises(ValueError):
            world.add_left(root, 4)

    def test_double_root_raises(self):
        world = TreeWorld()
        world.set_root(5)
        with pytest.raises(ValueError):
            world.set_root(6)

    def test_inorder_traversal(self):
        world = TreeWorld()
        root = world.set_root(5)
        world.add_left(root, 3)
        world.add_right(root, 8)
        values = [node.value for node in world.inorder()]
        assert values == [3, 5, 8]

    def test_preorder_traversal(self):
        world = TreeWorld()
        root = world.set_root(5)
        world.add_left(root, 3)
        world.add_right(root, 8)
        values = [node.value for node in world.preorder()]
        assert values == [5, 3, 8]

    def test_postorder_traversal(self):
        world = TreeWorld()
        root = world.set_root(5)
        world.add_left(root, 3)
        world.add_right(root, 8)
        values = [node.value for node in world.postorder()]
        assert values == [3, 8, 5]

    def test_highlight_sets_state(self):
        world = TreeWorld()
        root = world.set_root(5)
        world.highlight(root, "current")
        assert root.state == "current"

    def test_reset_colors_restores_root_state(self):
        world = TreeWorld()
        root = world.set_root(5)
        left = world.add_left(root, 3)
        world.highlight(left, "current")
        world.reset_colors()
        assert root.state == "root"
        assert left.state == "default"

    def test_full_three_level_tree_traversal(self):
        world = TreeWorld()
        root = world.set_root(4)
        left = world.add_left(root, 2)
        right = world.add_right(root, 6)
        world.add_left(left, 1)
        world.add_right(left, 3)
        world.add_left(right, 5)
        world.add_right(right, 7)
        assert [n.value for n in world.inorder()] == [1, 2, 3, 4, 5, 6, 7]

    def test_nodes_property_lists_all(self):
        world = TreeWorld()
        root = world.set_root(5)
        world.add_left(root, 3)
        assert len(world.nodes) == 2

    def test_layout_spreads_nodes_horizontally(self):
        # Regression: nodes must not collapse onto the same x coordinate.
        world = TreeWorld(width=600, column_width=60)
        root = world.set_root(5)
        left = world.add_left(root, 3)
        right = world.add_right(root, 8)
        xs = sorted(n.center[0] for n in (left, root, right))
        assert xs[1] - xs[0] >= 30
        assert xs[2] - xs[1] >= 30

    def test_layout_centers_root(self):
        world = TreeWorld(width=600, column_width=60)
        root = world.set_root(5)
        world.add_left(root, 3)
        world.add_right(root, 8)
        assert root.center[0] == 300

    def test_layout_full_three_level_tree(self):
        world = TreeWorld(width=600, column_width=60)
        root = world.set_root(4)
        left = world.add_left(root, 2)
        right = world.add_right(root, 6)
        world.add_left(left, 1)
        world.add_right(left, 3)
        world.add_left(right, 5)
        world.add_right(right, 7)
        xs = sorted(n.center[0] for n in world.nodes)
        assert xs[0] < xs[-1] - 200
        assert root.center[0] == 300


# ---------------------------------------------------------------- GraphWorld


class TestGraphWorld:
    def test_add_node_and_get_node(self):
        world = GraphWorld()
        node = world.add_node("A", "A", (100, 100))
        assert node.name == "A"
        assert world.get_node("A") is node

    def test_duplicate_node_raises(self):
        world = GraphWorld()
        world.add_node("A")
        with pytest.raises(ValueError):
            world.add_node("A")

    def test_unknown_node_raises(self):
        world = GraphWorld()
        with pytest.raises(KeyError):
            world.get_node("X")

    def test_connect_creates_undirected_edge(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        b = world.add_node("B", position=(100, 0))
        world.connect(a, b)
        assert b in world.neighbors(a)
        assert a in world.neighbors(b)

    def test_double_edge_raises(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        b = world.add_node("B", position=(100, 0))
        world.connect(a, b)
        with pytest.raises(ValueError):
            world.connect(a, b)

    def test_self_loop_raises(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        with pytest.raises(ValueError):
            world.connect(a, a)

    def test_neighbors_for_disconnected_node(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        assert world.neighbors(a) == []

    def test_set_start_and_target_highlights_nodes(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        b = world.add_node("B", position=(100, 0))
        world.set_start(a)
        world.set_target(b)
        assert a.state == "start"
        assert b.state == "target"

    def test_highlight_node_by_name(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        world.highlight("A", "current")
        assert a.state == "current"

    def test_highlight_edge_between_nodes(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        b = world.add_node("B", position=(100, 0))
        world.connect(a, b)
        world.highlight_edge(a, b, "visited")
        edge = world.edges[0]
        from miniworlds_data.graph_world import EDGE_VISITED_COLOR
        assert edge.fill_color == EDGE_VISITED_COLOR

    def test_path_edges_highlights_path(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        b = world.add_node("B", position=(100, 0))
        c = world.add_node("C", position=(200, 0))
        world.connect(a, b)
        world.connect(b, c)
        world.path_edges(["A", "B", "C"])
        from miniworlds_data.graph_world import EDGE_PATH_COLOR
        assert world.edges[0].fill_color == EDGE_PATH_COLOR
        assert world.edges[1].fill_color == EDGE_PATH_COLOR

    def test_reset_colors_restores_start_target(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        b = world.add_node("B", position=(100, 0))
        world.set_start(a)
        world.set_target(b)
        world.highlight(a, "current")
        world.reset_colors()
        assert a.state == "start"
        assert b.state == "target"

    def test_nodes_and_edges_properties(self):
        world = GraphWorld()
        a = world.add_node("A", position=(0, 0))
        b = world.add_node("B", position=(100, 0))
        world.connect(a, b)
        assert len(world.nodes) == 2
        assert len(world.edges) == 1



# ------------------------------------------------------------------- Stepper


class TestStepper:
    @staticmethod
    def _count_to(n):
        def gen():
            for i in range(n):
                yield "tick", i
        return gen()

    def test_next_step_advances_and_returns_step(self):
        stepper = Stepper(self._count_to(3))
        assert stepper.next_step() == ("tick", 0)
        assert stepper.next_step() == ("tick", 1)
        assert stepper.step_index == 1

    def test_next_step_returns_none_when_finished(self):
        stepper = Stepper(self._count_to(1))
        stepper.next_step()
        assert stepper.next_step() is None
        assert stepper.finished is True

    def test_steps_recorded_in_history(self):
        stepper = Stepper(self._count_to(3))
        stepper.next_step()
        stepper.next_step()
        assert stepper.steps == [("tick", 0), ("tick", 1)]

    def test_on_step_callback_invoked(self):
        applied = []
        stepper = Stepper(self._count_to(2), on_step=applied.append)
        stepper.next_step()
        stepper.next_step()
        assert applied == [("tick", 0), ("tick", 1)]

    def test_on_frame_throttles_by_frames_per_step(self):
        stepper = Stepper(self._count_to(5), frames_per_step=3)
        results = [stepper.on_frame() for _ in range(7)]
        # steps occur at frame 3 and frame 6
        assert results == [None, None, ("tick", 0), None, None, ("tick", 1), None]

    def test_prev_step_requires_on_reset_and_replays(self):
        state = []

        def reset():
            state.clear()

        stepper = Stepper(
            self._count_to(3),
            on_step=state.append,
            on_reset=reset,
        )
        stepper.next_step()
        stepper.next_step()
        assert state == [("tick", 0), ("tick", 1)]

        undone = stepper.prev_step()
        assert undone == ("tick", 1)
        assert state == [("tick", 0)]  # replayed after reset

    def test_prev_step_at_beginning_returns_none(self):
        stepper = Stepper(self._count_to(3), on_step=lambda _: None, on_reset=lambda: None)
        assert stepper.prev_step() is None

    def test_reset_requires_on_reset_and_clears_state(self):
        state = []
        stepper = Stepper(
            self._count_to(3),
            on_step=state.append,
            on_reset=state.clear,
        )
        stepper.next_step()
        stepper.next_step()
        stepper.reset()
        assert state == []
        assert stepper.step_index == -1

    def test_forward_after_backward_reuses_history_without_new_pulls(self):
        stepper = Stepper(self._count_to(3), on_step=lambda _: None, on_reset=lambda: None)
        stepper.next_step()  # index 0
        stepper.next_step()  # index 1
        stepper.prev_step()  # index 0
        history_len = len(stepper.steps)
        # Stepping forward again must reuse history, not pull a new step
        stepper.next_step()
        assert stepper.step_index == 1
        assert len(stepper.steps) == history_len

    def test_goto_forward_advances(self):
        stepper = Stepper(self._count_to(5))
        stepper.goto(2)
        assert stepper.step_index == 2
        assert stepper.steps[2] == ("tick", 2)

    def test_goto_backward_replays(self):
        state = []
        stepper = Stepper(
            self._count_to(5),
            on_step=state.append,
            on_reset=state.clear,
        )
        stepper.goto(3)
        assert len(state) == 4
        stepper.goto(1)
        assert state == [("tick", 0), ("tick", 1)]

    def test_goto_past_end_stops_at_finish(self):
        stepper = Stepper(self._count_to(2))
        stepper.goto(10)
        assert stepper.finished is True
        assert stepper.step_index == 1

    def test_run_requires_world(self):
        stepper = Stepper(self._count_to(2))
        with pytest.raises(ValueError):
            stepper.run()
