import heapq
from typing import ClassVar


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

    def pathfinder(self, weighted: bool = False) -> list[Zone]:
        """Check for valid path from start to end; return path if found."""

        if self.start._type == "blocked" or self.end._type == "blocked":
            return []

        def rebuild_path(
            parents_dict: dict[str, str | None], start: str, end: str
        ) -> list[Zone]:
            """Rebuild path from start to end using parent dictionary."""
            path = []
            current: str | None = end
            while current:
                path.append(self.zones[current])
                current = parents_dict[current]
            return path[::-1]

        visited: set[str] = {self.start.name}
        queue = [self.start]
        parents_dict: dict[str, str | None] = {self.start.name: None}

        move_cost: dict[str, float] = {
            "normal": 1.0,
            "priority": 1.0,
            "restricted": 2.0,
        }

        if weighted:
            p_queued_zones: list[tuple[float, str]] = [(0, self.start.name)]
            total_dist_to_zone: dict[str, float] = {self.start.name: 0}

            while p_queued_zones:
                current_cost, current_name = heapq.heappop(p_queued_zones)

                if current_name == self.end.name:
                    return rebuild_path(parents_dict, self.start.name, self.end.name)
                if current_cost > total_dist_to_zone.get(current_name, float("inf")):
                    continue
                zone_object = self.zones[current_name]
                for neighbor_candidate, _ in self.get_neighbors(zone_object):
                    if neighbor_candidate._type == "blocked":
                        continue
                    potential_move_cost = move_cost.get(neighbor_candidate._type, 1.0)
                    bias = -0.1 if neighbor_candidate._type == "priority" else 0.0
                    potential_move_cost += bias
                    potential_total_dist = current_cost + potential_move_cost
                    if potential_total_dist < total_dist_to_zone.get(
                        neighbor_candidate.name, float("inf")
                    ):
                        total_dist_to_zone[neighbor_candidate.name] = (
                            potential_total_dist
                        )
                        parents_dict[neighbor_candidate.name] = current_name
                        heapq.heappush(
                            p_queued_zones,
                            (potential_total_dist, neighbor_candidate.name),
                        )
            return []

        while queue:
            current_zone = queue.pop(0)
            if current_zone == self.end:
                return rebuild_path(parents_dict, self.start.name, self.end.name)
            for neighbor, _ in self.get_neighbors(current_zone):
                if neighbor.name not in visited and neighbor._type != "blocked":
                    visited.add(neighbor.name)
                    queue.append(neighbor)
                    parents_dict[neighbor.name] = current_zone.name
        return []


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


class Visualizer:
    """adds colors to zone names."""

    RESET = "\033[0m"

    COLORS: ClassVar[dict[str, str]] = {
        "red": "\033[91m",
        "crimson": "\033[31m",
        "darkred": "\033[31m",
        "maroon": "\033[31m",
        "green": "\033[92m",
        "lime": "\033[92m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "yellow": "\033[93m",
        "gold": "\033[93m",
        "orange": "\033[33m",
        "brown": "\033[33m",
        "purple": "\033[35m",
        "magenta": "\033[95m",
        "violet": "\033[35m",
        "gray": "\033[90m",
        "black": "\033[30m",
    }

    def colorize(self, text: str, color_name: str) -> str:
        """Return the text wrapped in ANSI color codes."""
        color_code = self.COLORS.get(color_name.lower(), "")
        return f"{color_code}{text}{self.RESET}" if color_code else text
