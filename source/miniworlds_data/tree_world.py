from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from miniworlds import Circle, Line, Text, World


Color = Tuple[int, int, int] | Tuple[int, int, int, int]


DEFAULT_COLOR: Color = (130, 170, 200, 255)
VISITED_COLOR: Color = (90, 190, 110, 255)
CURRENT_COLOR: Color = (245, 200, 60, 255)
ROOT_COLOR: Color = (220, 60, 60, 255)
EDGE_COLOR: Color = (140, 140, 140, 255)
EDGE_VISITED_COLOR: Color = (90, 190, 110, 255)
TEXT_COLOR: Color = (20, 20, 20, 255)


class TreeNode(Circle):
    """A node actor in a :class:`TreeWorld`.

    Each node stores a value, optional left/right children, and a highlight
    state used during traversals. Edges to its children are drawn as lines.
    """

    def __init__(self, value: object, *, world: "TreeWorld", radius: int, color: Color):
        super().__init__((0, 0), radius, world=world)
        self.origin = "center"
        self.fill_color = color
        self.border = 2
        self.border_color = (255, 255, 255, 255)
        self.is_static = True
        self.value: object = value
        self.left: Optional[TreeNode] = None
        self.right: Optional[TreeNode] = None
        self._state: str = "default"
        self._label = Text((0, 0), str(value), world=world)
        self._label.origin = "center"
        self._label.color = TEXT_COLOR
        self._label.font_size = max(10, int(radius * 0.8))
        self._label.is_static = True

    @property
    def state(self) -> str:
        return self._state

    def set_state(self, state: str) -> None:
        self._state = state
        self.fill_color = _STATE_COLORS.get(state, DEFAULT_COLOR)

    def center_on(self, x: float, y: float) -> None:
        self.center = (x, y)
        self._label.center = (x, y)

    def remove_label(self) -> None:
        if self._label.world is not None:
            self._label.remove()


_STATE_COLORS = {
    "default": DEFAULT_COLOR,
    "visited": VISITED_COLOR,
    "current": CURRENT_COLOR,
    "root": ROOT_COLOR,
}


class TreeWorld(World):
    """Pixel world that visualizes a binary tree.

    Nodes are added as a root plus left/right children. The world computes a
    level-order layout automatically and exposes traversal-friendly highlight
    methods.

    Example:
        ::

            from miniworlds_data import TreeWorld

            world = TreeWorld()
            root = world.set_root(5)
            world.add_left(root, 3)
            world.add_right(root, 8)
            world.highlight(root, "current")
            world.run()
    """

    def __init__(
        self,
        *,
        width: int = 600,
        height: int = 400,
        node_radius: int = 22,
        level_height: int = 70,
        column_width: int = 60,
        background: Color = (250, 250, 250, 255),
    ):
        super().__init__(width, height)
        self.background.fill_color = background
        self._node_radius = node_radius
        self._level_height = level_height
        self._column_width = column_width
        self._root: Optional[TreeNode] = None
        self._all_nodes: List[TreeNode] = []
        self._edges: List[Line] = []

    @property
    def root(self) -> Optional[TreeNode]:
        return self._root

    @property
    def nodes(self) -> List[TreeNode]:
        return list(self._all_nodes)

    def set_root(self, value: object) -> TreeNode:
        """Create the root node and return it."""
        if self._root is not None:
            raise ValueError("root already set")
        node = TreeNode(value, world=self, radius=self._node_radius, color=ROOT_COLOR)
        node.set_state("root")
        self._root = node
        self._all_nodes.append(node)
        self._relayout()
        return node

    def add_left(self, parent: TreeNode, value: object) -> TreeNode:
        """Add a left child to ``parent`` and return it."""
        if parent.left is not None:
            raise ValueError("left child already exists")
        node = self._create_child(parent, value)
        parent.left = node
        self._relayout()
        return node

    def add_right(self, parent: TreeNode, value: object) -> TreeNode:
        """Add a right child to ``parent`` and return it."""
        if parent.right is not None:
            raise ValueError("right child already exists")
        node = self._create_child(parent, value)
        parent.right = node
        self._relayout()
        return node

    def _create_child(self, parent: TreeNode, value: object) -> TreeNode:
        node = TreeNode(value, world=self, radius=self._node_radius, color=DEFAULT_COLOR)
        self._all_nodes.append(node)
        return node

    def highlight(self, node: TreeNode, state: str = "current") -> None:
        """Highlight a node with the given state.

        Args:
            node: Node to highlight.
            state: One of ``default``, ``visited``, ``current``, ``root``.
        """
        node.set_state(state)

    def highlight_edge(self, parent: TreeNode, child: TreeNode, visited: bool = True) -> None:
        """Color the edge between ``parent`` and ``child`` as visited/unvisited."""
        for edge in self._edges:
            if self._edge_matches(edge, parent, child):
                edge.fill_color = EDGE_VISITED_COLOR if visited else EDGE_COLOR
                return

    @staticmethod
    def _edge_matches(edge: Line, parent: TreeNode, child: TreeNode) -> bool:
        if not hasattr(edge, "_endpoints"):
            return False
        p, c = edge._endpoints  # type: ignore[attr-defined]
        return (p is parent and c is child) or (p is child and c is parent)

    def reset_colors(self) -> None:
        """Reset every node to its default/root state and edges to default color."""
        for node in self._all_nodes:
            node.set_state("root" if node is self._root else "default")
        for edge in self._edges:
            edge.fill_color = EDGE_COLOR

    # -- traversal helpers (non-visual) --------------------------------

    def inorder(self) -> List[TreeNode]:
        """Return nodes in in-order sequence."""
        result: List[TreeNode] = []
        self._inorder(self._root, result)
        return result

    def preorder(self) -> List[TreeNode]:
        """Return nodes in pre-order sequence."""
        result: List[TreeNode] = []
        self._preorder(self._root, result)
        return result

    def postorder(self) -> List[TreeNode]:
        """Return nodes in post-order sequence."""
        result: List[TreeNode] = []
        self._postorder(self._root, result)
        return result

    def _inorder(self, node: Optional[TreeNode], acc: List[TreeNode]) -> None:
        if node is None:
            return
        self._inorder(node.left, acc)
        acc.append(node)
        self._inorder(node.right, acc)

    def _preorder(self, node: Optional[TreeNode], acc: List[TreeNode]) -> None:
        if node is None:
            return
        acc.append(node)
        self._preorder(node.left, acc)
        self._preorder(node.right, acc)

    def _postorder(self, node: Optional[TreeNode], acc: List[TreeNode]) -> None:
        if node is None:
            return
        self._postorder(node.left, acc)
        self._postorder(node.right, acc)
        acc.append(node)

    # -- layout --------------------------------------------------------

    def _relayout(self) -> None:
        self._clear_edges()
        if self._root is None:
            return
        positions: Dict[TreeNode, float] = {}
        self._assign_x_positions(self._root, 0, positions)
        depth = self._assign_depths(self._root, 0, {})
        # In-order offsets run from 0 to max; center the tree around the
        # world midpoint and space columns by _column_width pixels.
        mid = (max(positions.values()) if positions else 0) / 2
        for node, x_offset in positions.items():
            depth_n = depth.get(node, 0)
            y = 40 + depth_n * self._level_height
            x = self.width / 2 + (x_offset - mid) * self._column_width
            node.center_on(x, y)
        self._draw_edges(self._root)

    def _assign_x_positions(
        self,
        node: Optional[TreeNode],
        x: float,
        positions: Dict[TreeNode, float],
    ) -> float:
        if node is None:
            return x
        x = self._assign_x_positions(node.left, x, positions)
        positions[node] = x
        return self._assign_x_positions(node.right, x + 1, positions)

    def _assign_depths(
        self, node: Optional[TreeNode], depth: int, acc: Dict[TreeNode, int]
    ) -> Dict[TreeNode, int]:
        if node is None:
            return acc
        acc[node] = depth
        self._assign_depths(node.left, depth + 1, acc)
        self._assign_depths(node.right, depth + 1, acc)
        return acc

    def _clear_edges(self) -> None:
        for edge in self._edges:
            edge.remove()
        self._edges.clear()

    def _draw_edges(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        for child in (node.left, node.right):
            if child is not None:
                edge = Line(node.center, child.center, world=self)
                edge.fill_color = EDGE_COLOR
                edge.border = 2
                edge.is_static = True
                edge._endpoints = (node, child)  # type: ignore[attr-defined]
                edge.layer = 0
                node.layer = 1
                child.layer = 1
                self._edges.append(edge)
                self._draw_edges(child)
