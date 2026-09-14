class Zone:
    """Represents a hub/zone in the network."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str = "none",
        _type: str = "normal",
        max_drones: int = 1,
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self._type = _type
        self.max_drones = max_drones
        self.current_drones: list[int] = []

    def __repr__(self) -> str:
        return f"Zone({self.name}, {self._type})"


class Connection:
    """Represents a bidirectional connection between two zones."""

    def __init__(
        self,
        zone_a: Zone,
        zone_b: Zone,
        max_link_capacity: int = 1,
    ) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity
        self.current_drones: list[int] = []

    def other(self, zone: Zone) -> Zone:
        """Return the other end of the connection."""
        return self.zone_b if zone == self.zone_a else self.zone_a

    def __repr__(self) -> str:
        return (
            f"Connection({self.zone_a.name}-{self.zone_b.name}, "
            f"cap={self.max_link_capacity})"
        )


class Graph:
    """Represents the complete network of zones and connections."""

    def __init__(
        self,
        start: Zone,
        end: Zone,
        zones: dict[str, Zone],
        connections_lst: list[Connection],
        nb_drones: int,
    ) -> None:
        self.start = start
        self.end = end
        self.nb_drones = nb_drones
        self.zones = zones
        self.connections_lst = connections_lst
        self.adj: dict[str, list[Connection]] = {name: [] for name in self.zones}

        # loop through connections take both a/b names as dict keys
        # append connection to list of connections for that zone (dict value)
        for conn in self.connections_lst:
            self.adj[conn.zone_a.name].append(conn)
            self.adj[conn.zone_b.name].append(conn)

    def get_neighbors(self, zone: Zone) -> list[tuple[Zone, Connection]]:
        """Return (neighbor_zone, connection) pairs for a given zone."""
        return [(conn.other(zone), conn) for conn in self.adj.get(zone.name, [])]

    def pathfinder(self, save_path: bool) -> bool | list[Zone]:
        """Check for valid path from start to end; return path if True."""
        if self.start._type == "blocked" or self.end._type == "blocked":
            return [] if save_path else False

        visited: set[str] = {self.start.name}
        queue = [self.start]
        parent: dict[str, str | None] = {self.start.name: None} if save_path else {}

        def rebuild_path(
            parent: dict[str, str | None], start: str, end: str
        ) -> list[Zone]:
            """Rebuild path from start to end using parent dictionary."""
            path = []
            current: str | None = end
            while current is not None:
                path.append(self.zones[current])
                current = parent[current]
            return path[::-1]  # Reverse path to get it from start to end

        while queue:
            current_zone = queue.pop(0)
            if current_zone == self.end:
                return (
                    rebuild_path(parent, self.start.name, self.end.name)
                    if save_path
                    else True
                )
            for neighbor, _ in self.get_neighbors(current_zone):
                if neighbor.name not in visited and neighbor._type != "blocked":
                    visited.add(neighbor.name)
                    queue.append(neighbor)
                    if save_path:
                        parent[neighbor.name] = current_zone.name
        return [] if save_path else False


class Drone:
    """Represents a drone in the network."""

    def __init__(self, drone_id: int, path: list[Zone]) -> None:
        self.drone_id = drone_id
        self.path: list[Zone] = path
        self.steps_taken = 0

    def __repr__(self) -> str:
        return f"Drone({self.drone_id}, at {self.current_zone.name})"

    # dynamic property/attribue, read-only, protects data synchronization.
    @property
    def current_zone(self) -> Zone:
        """Return the current zone of the drone."""
        return self.path[self.steps_taken]

    @property
    def next_zone(self) -> Zone | None:
        """Return the next zone in the path, if available."""
        if self.steps_taken + 1 < len(self.path):
            return self.path[self.steps_taken + 1]
        return None

    @property
    def has_arrived(self) -> bool:
        """Check if the drone has reached its destination."""
        return self.steps_taken >= len(self.path) - 1
