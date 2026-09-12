from dataclasses import dataclass

from graph import Graph, Zone

zone_keys = ("zone", "color", "max_drones")
connection_keys = ("max_link_capacity",)
zone_types = ("normal", "restricted", "priority", "blocked")

cnct_keys = "max_link_capacity"

clr_set = {
    "Red",
    "Blue",
    "Green",
    "Yellow",
    "Orange",
    "Purple",
    "Pink",
    "Brown",
    "Black",
    "White",
    "Gray",
}


@dataclass
class Metadata:
    color: str | None = None
    type: str | None = None
    max_drones: int | None = None
    max_cap: int | None = None


class ParseError(Exception):
    pass


class Parser:
    def __init__(self):
        self.nb_drones_seen = False
        self.zones: dict[str, Zone] = {}
        self.nb_drones = 0
        self.connections: list[tuple[Zone, Zone, int]] = []
        self.start: Zone | None = None
        self.end: Zone | None = None

    def is_pos_int(self, value):
        try:
            int_value = int(value)
        except ValueError:
            raise ParseError(
                "Error: nb_drones and max_drones must be integers, exiting"
            )
        if int_value < 0:
            raise ParseError(
                "Error: nb_drones and max_drones must be positive, exiting"
            )
        return int_value

    def is_int(self, coordinate):
        try:
            inted_coord = int(coordinate)
            return inted_coord
        except ValueError:
            raise (ParseError("Error: all coordinates have to be integers"))

    def split_metadata(self, metadata: str, keys) -> Metadata:
        if not (metadata[0] == "[" and metadata[-1] == "]"):
            raise ParseError("Error: metadata must be in brackets")

        color = zone_type = max_drones = max_cap = None

        for item in metadata[1:-1].split():
            key, custom = item.split("=", 1)
            if key not in keys:
                continue
            if key == "color":
                all_alpha = all(letter.isalpha() for letter in custom)
                if not all_alpha:
                    raise ParseError("Error: Color must be a single-word string")
                color = custom
            elif key == "zone":
                if custom not in zone_types:
                    raise ParseError("Error: invalid zone type")
                zone_type = custom
            elif key == "max_drones":
                max_drones = self.is_pos_int(custom)
            elif key == "max_link_capacity":
                max_cap = self.is_pos_int(custom)

        return Metadata(
            color=color, type=zone_type, max_drones=max_drones, max_cap=max_cap
        )

    def parse_zones(self, key, value) -> None:
        metadata_str = ""
        if "[" in value and value.endswith("]"):
            value_raw, metadata_str = value.split("[", 1)
            metadata_str = "[" + metadata_str
        else:
            value_raw = value
        parts = value_raw.split()
        if key in ("start_hub", "end_hub") or key == "hub":
            name, x, y = parts
        else:
            raise ParseError(f"Error: Invalid Key: {key}")
        if "-" in name:
            raise ParseError("Error: Zone name can't have '-'")
        x, y = self.is_int(x), self.is_int(y)

        meta = self.split_metadata(metadata_str, zone_keys)
        color = meta.color if meta.color is not None else "white"
        zone_type = meta.type if meta.type is not None else "normal"

        if key == "start_hub":
            self.start = Zone(name, x, y)
            self.zones[name] = self.start

        elif key == "end_hub":
            self.end = Zone(name, x, y)
            self.zones[name] = self.end

        elif key == "hub":
            self.zones[name] = Zone(name, x, y, color, zone_type)
        else:
            raise (ParseError(f"Error: Invalid Key: {key}"))

    def parse_connection(self, value) -> None:
        # example of connection line: bottleneck-wide_area [max_link_capacity=4]
        # need to to check if names exist in self.zones or raise error if not
        names, metadata = value.split(" ")
        name1, name2 = names.split("-")
        meta = self.split_metadata(metadata.strip(), connection_keys)
        max_cap = meta.max_cap if meta.max_cap is not None else 1
        try:
            zone1 = self.zones[name1]
            zone2 = self.zones[name2]
            self.connections.append((zone1, zone2, max_cap))
        except KeyError:
            raise ParseError(
                f"Error: Connection between {name1} and {name2} cannot be created because one or both zones do not exist"
            )

    def parse_map(self, map):
        with map.open() as map_file:
            raw_lines = map_file.readlines()
            print("raw_lines: ", raw_lines)
            for line in raw_lines:
                cleaned = line.split("#")[0].strip()
                if cleaned:
                    if cleaned.startswith("nb_drones"):
                        self.nb_drones_seen = True
                    if not self.nb_drones_seen:
                        raise (ParseError("nb_drones must be the first config"))
                    key, value = cleaned.split(":")
                    if key.strip() == "nb_drones":
                        self.nb_drones = self.is_pos_int(value.strip())
                    if "hub" in key:
                        self.parse_zones(key.strip(), value)
                    if key.strip() == "connection":
                        self.connection = self.parse_connection(value.strip())
            return (
                Graph(self.start, self.end, self.zones, self.connections),
                self.nb_drones,
            )
