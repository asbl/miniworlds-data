from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from miniworlds import Circle, Line, Text, World


Color = Tuple[int, int, int] | Tuple[int, int, int, int]


DEFAULT_COLOR: Color = (130, 170, 200, 255)
VISITED_COLOR: Color = (90, 190, 110, 255)
CURRENT_COLOR: Color = (245, 200, 60, 255)
FRONTIER_COLOR: Color = (160, 110, 220, 255)
START_COLOR: Color = (220, 60, 60, 255)
TARGET_COLOR: Color = (60, 140, 210, 255)
PATH_COLOR: Color = (90, 190, 110, 255)
EDGE_COLOR: Color = (160, 160, 160, 255)
EDGE_VISITED_COLOR: Color = (90, 190, 110, 255)
EDGE_PATH_COLOR: Color = (220, 120, 50, 255)
TEXT_COLOR: Color = (20, 20, 20, 255)


class GraphNode(Circle):
    """A node actor in a :class:`GraphWorld`."""

    def __init__(self, name: str, value: object, *, world: "GraphWorld", radius: int, color: Color):
        super().__init__((0, 0), radius, world=world)
        self.origin = "center"
        self.fill_color = color
        self.border = 2
        self.border_color = (255, 255, 255, 255)
        self.is_static = True
        self.name: str = name
        self.value: object = value
        self._state: str = "default"
        self._label = Text((0, 0), str(value), world=world)
        self._label.origin = "center"
        self._label.color = TEXT_COLOR
        self._label.font_size = max(10, int(radius * 0.8))
        self._label.is_static = True

    @property
    def state(self) -> str:
        return self._state

    def set_state(self, state: str, color: Optional[Color] = None) -> None:
        self._state = state
        self.fill_color = color if color is not None else _STATE_COLORS.get(state, DEFAULT_COLOR)

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
    "frontier": FRONTIER_COLOR,
    "start": START_COLOR,
    "target": TARGET_COLOR,
    "path": PATH_COLOR,
}


class GraphEdge(Line):
    """An edge actor in a :class:`GraphWorld` connecting two nodes."""

    def __init__(self, source: GraphNode, target: GraphNode, *, world: "GraphWorld"):
        super().__init__(source.center, target.center, world=world)
        self.fill_color = EDGE_COLOR
        self.border = 2
        self.is_static = True
        self.source = source
        self.target = target
        self.layer = 0
        source.layer = 1
        target.layer = 1

    def refresh(self) -> None:
        self.start_position = self.source.center
        self.end_position = self.target.center

    def set_state(self, state: str, color: Optional[Color] = None) -> None:
        if color is not None:
            self.fill_color = color
        elif state == "visited":
            self.fill_color = EDGE_VISITED_COLOR
        elif state == "path":
            self.fill_color = EDGE_PATH_COLOR
        else:
            self.fill_color = EDGE_COLOR


class GraphWorld(World):
    """Pixel world that visualizes an undirected graph.

    Nodes are added by name at explicit positions and connected by edges. The
    world is well-suited for pathfinding (BFS/DFS) and traversal tasks.

    Example:
        ``GraphWorld()`` creates a drawing area for named nodes. Use
        ``add_node(...)`` and ``connect(...)`` to build the graph, then call
        ``set_start(...)``, ``set_target(...)``, or ``highlight(...)`` while an
        algorithm runs.
    """

    def __init__(
        self,
        *,
        width: int = 600,
        height: int = 400,
        node_radius: int = 22,
        background: Color = (250, 250, 250, 255),
    ):
        super().__init__(width, height)
        self.background.fill_color = background
        self._node_radius = node_radius
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
        self._adjacency: Dict[str, set] = {}
        self._start: Optional[str] = None
        self._target: Optional[str] = None

    @property
    def nodes(self) -> List[GraphNode]:
        return list(self._nodes.values())

    @property
    def edges(self) -> List[GraphEdge]:
        return list(self._edges)

    def add_node(self, name: str, value: object = None, position: Optional[Tuple[float, float]] = None) -> GraphNode:
        """Add a node and return it.

        Args:
            name: Unique node identifier.
            value: Displayed value (defaults to ``name``).
            position: Center position. Defaults to the world center.
        """
        if name in self._nodes:
            raise ValueError(f"node {name!r} already exists")
        value = name if value is None else value
        node = GraphNode(name, value, world=self, radius=self._node_radius, color=DEFAULT_COLOR)
        self._nodes[name] = node
        self._adjacency[name] = set()
        x, y = position if position is not None else (self.width / 2, self.height / 2)
        node.center_on(x, y)
        return node

    def get_node(self, name: str) -> GraphNode:
        """Return the node with the given name."""
        try:
            return self._nodes[name]
        except KeyError:
            raise KeyError(f"unknown node {name!r}") from None

    def connect(self, source: str | GraphNode, target: str | GraphNode) -> GraphEdge:
        """Connect two nodes with an undirected edge and return it."""
        src = self._coerce_node(source)
        dst = self._coerce_node(target)
        if src is dst:
            raise ValueError("cannot connect a node to itself")
        if dst.name in self._adjacency[src.name]:
            raise ValueError(f"edge {src.name}-{dst.name} already exists")
        self._adjacency[src.name].add(dst.name)
        self._adjacency[dst.name].add(src.name)
        edge = GraphEdge(src, dst, world=self)
        self._edges.append(edge)
        return edge

    def neighbors(self, node: str | GraphNode) -> List[GraphNode]:
        """Return the neighbors of a node (unordered)."""
        name = self._coerce_name(node)
        return [self._nodes[n] for n in self._adjacency[name]]

    def set_start(self, node: str | GraphNode) -> None:
        """Mark a node as the search start (red)."""
        name = self._coerce_name(node)
        if self._start is not None and self._start != name:
            self.get_node(self._start).set_state("default")
        self._start = name
        self.get_node(name).set_state("start")

    def set_target(self, node: str | GraphNode) -> None:
        """Mark a node as the search target (blue)."""
        name = self._coerce_name(node)
        if self._target is not None and self._target != name:
            self.get_node(self._target).set_state("default")
        self._target = name
        self.get_node(name).set_state("target")

    def highlight(self, node: str | GraphNode, state: str = "current", color: Optional[Color] = None) -> None:
        """Highlight a node with a named state or an explicit color.

        Args:
            node: Node name or instance.
            state: One of ``default``, ``visited``, ``current``, ``frontier``,
                ``start``, ``target``, ``path``.
            color: Optional explicit color overriding the state's default color.
        """
        self._coerce_node(node).set_state(state, color)

    def highlight_edge(self, source: str | GraphNode, target: str | GraphNode, state: str = "visited", color: Optional[Color] = None) -> None:
        """Highlight the edge between two nodes."""
        src_name = self._coerce_name(source)
        dst_name = self._coerce_name(target)
        for edge in self._edges:
            names = {edge.source.name, edge.target.name}
            if names == {src_name, dst_name}:
                edge.set_state(state, color)
                return

    def reset_colors(self) -> None:
        """Reset every node to its start/target/default state and edges to default color."""
        for name, node in self._nodes.items():
            if name == self._start:
                node.set_state("start")
            elif name == self._target:
                node.set_state("target")
            else:
                node.set_state("default")
        for edge in self._edges:
            edge.set_state("default")

    def path_edges(self, path: Iterable[str | GraphNode]) -> None:
        """Highlight the edges along a sequence of node names/instances as a path."""
        names = [self._coerce_name(n) for n in path]
        for edge in self._edges:
            edge.set_state("default")
        for a, b in zip(names, names[1:]):
            self.highlight_edge(a, b, "path")

    def _coerce_node(self, node: str | GraphNode) -> GraphNode:
        if isinstance(node, GraphNode):
            return node
        return self.get_node(node)

    def _coerce_name(self, node: str | GraphNode) -> str:
        if isinstance(node, GraphNode):
            return node.name
        return node
