import sys
from dataclasses import dataclass
from pathlib import Path

from graph import Connection, Graph, Zone

connection_keys = ("max_link_capacity",)
zone_types = ("normal", "restricted", "priority", "blocked")


@dataclass
class Metadata:
    color: str | None = None
    type: str | None = None
    max_drones: int | None = None
    max_cap: int | None = None


class ParseError(Exception):
    pass


class Parser:
    def __init__(self) -> None:
        self.start_count = 0
        self.end_count = 0
        self.zones: dict[str, Zone] = {}
        self.nb_drones = 0
        self.connections_lst: list[Connection] = []
        self.start: Zone | None = None
        self.end: Zone | None = None
        self.seen_connections: set[tuple[str, ...]] = set()
        self.nb_drones_seen = False
        self.connections_started = False

    def is_pos_int(
        self, value: str, line_num: int, field_name: str = "value"
    ) -> int:
        try:
            int_value = int(value)
        except ValueError:
            raise ParseError(
                f"Line {line_num}: {field_name} must be an integer"
            )
        if int_value <= 0:
            raise ParseError(
                f"Line {line_num}: {field_name} must be a positive integer"
            )
        return int_value

    def is_int(self, coordinate: str, line_num: int) -> int:
        try:
            return int(coordinate)
        except ValueError:
            raise ParseError(f"Line {line_num}: Coordinates must be integers")

    def parse_metadata(
        self, metadata: str, line_num: int, is_zone: bool = False
    ) -> Metadata:
        metadata_keys = ("zone", "color", "max_drones")

        if not (metadata[0] == "[" and metadata[-1] == "]"):
            raise ParseError(f"Line {line_num}: Metadata must be in brackets")

        color = zone_type = max_drones = max_cap = None
        seen_keys: set[str] = set()

        for item in metadata[1:-1].split():
            if "=" not in item:
                raise ParseError(
                    f"Line {line_num}: Invalid metadata syntax '{item}'. "
                    "Expected 'key=value'"
                )
            key, custom = item.split("=", 1)
            key, custom = key.strip(), custom.strip()

            if not key or not custom:
                raise ParseError(
                    f"Line {line_num}: Metadata key and value cannot be empty"
                )

            if key in seen_keys:
                raise ParseError(
                    f"Line {line_num}: Duplicate metadata key: {key}"
                )
            seen_keys.add(key)

            if is_zone and key not in metadata_keys:
                raise ParseError(
                    f"Line {line_num}: Invalid metadata key for zone: {key}"
                )
            elif not is_zone and key not in connection_keys:
                raise ParseError(
                    f"Line {line_num}: Invalid metadata key for "
                    f"connection: {key}"
                )
            if key == "color":
                all_alpha = all(letter.isalpha() for letter in custom)
                if not all_alpha:
                    raise ParseError(
                        f"Line {line_num}: Color must be a single-word string"
                    )
                color = custom
            elif key == "zone":
                if custom not in zone_types:
                    raise ParseError(
                        f"Line {line_num}: Invalid zone type '{custom}'"
                    )
                zone_type = custom
            elif key == "max_drones":
                max_drones = self.is_pos_int(custom, line_num, "max_drones")
            elif key == "max_link_capacity":
                max_cap = self.is_pos_int(
                    custom, line_num, "max_link_capacity"
                )

        return Metadata(
            color=color, type=zone_type, max_drones=max_drones, max_cap=max_cap
        )

    def parse_zones(self, key: str, value: str, line_num: int) -> None:
        metadata_str = ""
        if "[" in value:
            if not value.strip().endswith("]"):
                raise ParseError(
                    f"Line {line_num}: Metadata must be in brackets"
                )
            name_coordinates, metadata_str = value.split("[", 1)
            metadata_str = "[" + metadata_str
        else:
            name_coordinates = value
        name_coordinates_lst = name_coordinates.split()
        if len(name_coordinates_lst) != 3:
            raise ParseError(
                f"Line {line_num}: Invalid number of arguments for {key}. "
                "Expected 3 arguments (name, x, y)."
            )

        if key == "start_hub":
            name, x_raw, y_raw = name_coordinates_lst
            self.start_count += 1
            if self.start_count > 1:
                raise ParseError(
                    f"Line {line_num}: Multiple start_hub definitions found"
                )
        elif key == "end_hub":
            name, x_raw, y_raw = name_coordinates_lst
            self.end_count += 1
            if self.end_count > 1:
                raise ParseError(
                    f"Line {line_num}: Multiple end_hub definitions found"
                )
        elif key == "hub":
            name, x_raw, y_raw = name_coordinates_lst
        else:
            raise ParseError(f"Line {line_num}: Invalid Key: {key}")

        if "-" in name or " " in name:
            raise ParseError(
                f"Line {line_num}: Zone name can't have '-' or spaces"
            )
        x = self.is_int(x_raw, line_num)
        y = self.is_int(y_raw, line_num)

        meta = (
            self.parse_metadata(metadata_str, line_num, is_zone=True)
            if metadata_str
            else Metadata()
        )
        color = meta.color if meta.color is not None else "none"
        zone_type = meta.type if meta.type is not None else "normal"
        max_drones: int = meta.max_drones if meta.max_drones is not None else 1
        if key == "start_hub":
            self.start = Zone(
                name, x, y, color, zone_type, max_drones=sys.maxsize
            )
            if name not in self.zones:
                self.zones[name] = self.start
            else:
                raise ParseError(
                    f"Line {line_num}: Zone name '{name}' already exists"
                )
        elif key == "end_hub":
            self.end = Zone(
                name, x, y, color, zone_type, max_drones=sys.maxsize
            )
            if name not in self.zones:
                self.zones[name] = self.end
            else:
                raise ParseError(
                    f"Line {line_num}: Zone name '{name}' already exists"
                )
        elif key == "hub":
            if name not in self.zones:
                self.zones[name] = Zone(
                    name, x, y, color, zone_type, max_drones
                )
            else:
                raise ParseError(
                    f"Line {line_num}: Zone name '{name}' already exists"
                )

    def parse_connection(self, value: str, line_num: int) -> None:
        metadata_str = ""
        if "[" in value:
            if not value.strip().endswith("]"):
                raise ParseError(
                    f"Line {line_num}: Metadata must be in brackets"
                )
            names, metadata_str = value.split("[", 1)
            metadata_str = "[" + metadata_str
        else:
            names = value

        names = names.strip()
        if "-" not in names or names.count("-") != 1:
            raise ParseError(
                f"Line {line_num}: Invalid connection format: {names}"
            )
        name1, name2 = names.split("-")
        if name1 == name2:
            raise ParseError(
                f"Line {line_num}: Self-connection is forbidden: {name1}"
            )

        new_conn = tuple(sorted([name1, name2]))
        if new_conn in self.seen_connections:
            raise ParseError(
                f"Line {line_num}: Duplicate connection between "
                f"{name1} and {name2}"
            )
        self.seen_connections.add(new_conn)

        meta = (
            self.parse_metadata(metadata_str, line_num, is_zone=False)
            if metadata_str
            else Metadata()
        )
        max_cap = meta.max_cap if meta.max_cap is not None else 1
        try:
            zone1 = self.zones[name1]
            zone2 = self.zones[name2]
            self.connections_lst.append(Connection(zone1, zone2, max_cap))
        except KeyError:
            raise ParseError(
                f"Line {line_num}: Connection between {name1} and {name2} "
                "cannot be created because one or both zones do not exist"
            )

    def parse_map(self, map_path: Path) -> tuple[Graph, int]:
        self.nb_drones_seen = False
        self.connections_started = False
        with map_path.open() as map_file:
            for line_num, raw_line in enumerate(map_file, start=1):
                cleaned = raw_line.split("#")[0].strip()
                if not cleaned:
                    continue
                if cleaned.startswith("nb_drones"):
                    self.nb_drones_seen = True
                if not self.nb_drones_seen:
                    raise ParseError(
                        f"Line {line_num}: nb_drones must be the first config"
                    )
                key, value = cleaned.split(":", 1)
                stripped_key = key.strip()
                stripped_val = value.strip()
                if stripped_key == "nb_drones":
                    self.nb_drones = self.is_pos_int(
                        stripped_val, line_num, "nb_drones"
                    )
                elif stripped_key in ("start_hub", "end_hub", "hub"):
                    if not self.nb_drones_seen:
                        raise ParseError(
                            f"Line {line_num}: nb_drones must be defined "
                            "before hubs"
                        )
                    if self.connections_started:
                        raise ParseError(
                            f"Line {line_num}: All hubs must be defined "
                            "before connections"
                        )
                    self.parse_zones(stripped_key, stripped_val, line_num)
                elif stripped_key == "connection":
                    if self.start is None or self.end is None:
                        raise ParseError(
                            f"Line {line_num}: start_hub and end_hub "
                            "must be defined before connections"
                        )
                    self.connections_started = True
                    self.parse_connection(stripped_val, line_num)
                else:
                    raise ParseError(
                        f"Line {line_num}: Unknown configuration key "
                        f"'{stripped_key}'"
                    )

            if self.start is None or self.end is None:
                raise ParseError(
                    "Error: Both start_hub and end_hub must be defined"
                )

            graph = Graph(
                self.start, self.end, self.zones, self.connections_lst
            )
            if not graph.pathfinder(save_path=False):
                raise ParseError(
                    "Error: Disconnected graph (no valid path from "
                    "start_hub to end_hub)"
                )

            return graph, self.nb_drones
