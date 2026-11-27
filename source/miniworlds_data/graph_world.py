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
        self.layer = 1
        self.name: str = name
        self.value: object = value
        self._state: str = "default"
        self._label = Text((0, 0), str(value), world=world)
        self._label.origin = "center"
        self._label.color = TEXT_COLOR
        self._label.font_size = max(10, int(radius * 0.8))
        self._label.is_static = True
        self._label.layer = 2

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
        self._adjacency: Dict[str, Dict[str, GraphEdge]] = {}
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
        x, y = position if position is not None else (self.width / 2, self.height / 2)
        value = name if value is None else value
        node = GraphNode(name, value, world=self, radius=self._node_radius, color=DEFAULT_COLOR)
        node.center_on(x, y)
        self._nodes[name] = node
        self._adjacency[name] = {}
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
        edge = GraphEdge(src, dst, world=self)
        self._adjacency[src.name][dst.name] = edge
        self._adjacency[dst.name][src.name] = edge
        self._edges.append(edge)
        return edge

    def neighbors(self, node: str | GraphNode) -> List[GraphNode]:
        """Return the neighbors of a node in the order they were connected."""
        name = self._coerce_name(node)
        return [self._nodes[n] for n in self._adjacency[name]]

    def set_start(self, node: str | GraphNode) -> None:
        """Mark the search start in red. A shared start and target stays blue."""
        name = self._coerce_name(node)
        previous = self._start
        self._start = name
        if previous is not None and previous != name:
            self.get_node(previous).set_state(self._endpoint_state(previous))
        self.get_node(name).set_state(self._endpoint_state(name))

    def set_target(self, node: str | GraphNode) -> None:
        """Mark a node as the search target (blue)."""
        name = self._coerce_name(node)
        previous = self._target
        self._target = name
        if previous is not None and previous != name:
            self.get_node(previous).set_state(self._endpoint_state(previous))
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
        edge = self._adjacency[src_name].get(dst_name)
        if edge is not None:
            edge.set_state(state, color)

    def reset_colors(self) -> None:
        """Reset every node to its start/target/default state and edges to default color."""
        for name, node in self._nodes.items():
            node.set_state(self._endpoint_state(name))
        for edge in self._edges:
            edge.set_state("default")

    def path_edges(self, path: Iterable[str | GraphNode]) -> None:
        """Highlight the edges along a sequence of node names or instances.

        Raises ``ValueError`` if consecutive nodes are not connected.
        """
        names = [self._coerce_name(n) for n in path]
        path_edges = []
        for source, target in zip(names, names[1:]):
            edge = self._adjacency[source].get(target)
            if edge is None:
                raise ValueError(f"no edge between {source!r} and {target!r}")
            path_edges.append(edge)
        for edge in self._edges:
            edge.set_state("default")
        for edge in path_edges:
            edge.set_state("path")

    def _endpoint_state(self, name: str) -> str:
        if name == self._target:
            return "target"
        if name == self._start:
            return "start"
        return "default"

    def _coerce_node(self, node: str | GraphNode) -> GraphNode:
        if isinstance(node, GraphNode):
            if node.world is not self or self._nodes.get(node.name) is not node:
                raise ValueError("node does not belong to this GraphWorld")
            return node
        return self.get_node(node)

    def _coerce_name(self, node: str | GraphNode) -> str:
        return self._coerce_node(node).name
