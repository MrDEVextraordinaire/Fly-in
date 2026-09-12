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

    def __str__(self) -> str:
        return f"Zone({self.name}, {self._type})"

    def __repr__(self) -> str:
        return self.__str__()


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

    def __str__(self) -> str:
        return (
            f"Connection({self.zone_a.name}-{self.zone_b.name}, "
            f"cap={self.max_link_capacity})"
        )

    def __repr__(self) -> str:
        return self.__str__()


class Graph:
    """Represents the complete network of zones and connections."""

    def __init__(
        self,
        start: Zone,
        end: Zone,
        zones: dict[str, Zone],
        connections: list[Connection],
    ) -> None:
        self.start = start
        self.end = end
        self.zones = zones
        self.connections = connections
        # Adjacency list: zone_name -> list of connections
        self.adj: dict[str, list[Connection]] = {name: [] for name in self.zones}
        for conn in self.connections:
            self.adj[conn.zone_a.name].append(conn)
            self.adj[conn.zone_b.name].append(conn)

    def get_neighbors(self, zone: Zone) -> list[tuple[Zone, Connection]]:
        """Return (neighbor_zone, connection) pairs for a given zone."""
        return [(conn.other(zone), conn) for conn in self.adj.get(zone.name, [])]
