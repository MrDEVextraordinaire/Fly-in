from dataclasses import dataclass
from graph import Graph

zone_keys = ("zone", "color", "max_drones")
zone_types = ("normal", "restricted", "priority", "blocked")

cnct_keys = (max_link_capacity)

clr_set = {
    "Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Pink", "Brown",
    "Black", "White", "Gray"
}



@dataclass
class Metadata:
	color: str
	type: str
	max_drones: int
	max_cap: int


class ParseError(Exception):
	pass


class Parser():
	def __init__(self):
		self.nb_drones_seen = False
		self.zones = {}
		self.nb_drones = 0
		self.connections = []
		self.start = {}
		self.end = {}

	def is_pos_int(self, value):
		try:
			int_value = int(value)
		except ValueError:
			raise ParseError("Error: nb_drones and max_drones must be integers, exiting")
		if int_value <= 0:
			raise ParseError("Error: nb_drones and max_drones must be positive, exiting")
		return int_value

	def is_int(self, coordinate):
		try:
			inted_coord = int(coordinate)
			return inted_coord
		except ValueError:
			raise (ParseError("Error: all coordinates have to be integers"))

	def split_metadata(self, metadata, keys):
		all_clrs_valid = True

		if metadata[0] == "[" and metadata[-1] == "]":
			meta_lst = metadata[1:-1].split()
			nb_keys = len(meta_lst)
			for i in range(nb_keys):
				key, custom = meta_lst[i].split('=', 1)
				if 	key in keys:
					if key == "color":
						if not custom.isalpha():
							raise(ParseError("Error: Color must be a single-word string"))
						if custom not in clr_set:
							all_clrs_valid = False
					if key == "zone":
						if custom not in zone_types:
							raise(ParseError("Error: invalid zone type"))
					if key == "max_drones":
						custom = is_pos_int(custom)
		else:
			raise(ParseError("Error: metadata must be in brackets"))
		

	def parse_zones(self, key, value):
		name, x, y, metadata = value.split(" ")
		if not all(letter not in " -" for letter in name):
			raise ParseError("Error: Zone name cant't have '-'")
		x, y = is_int(x.strip()), is_int(y.strip())
		meta = split_metadata(metadata.strip(), zone_keys)

		if key == "start_hub":
			self.start = Zone(name, x, y)

		elif key == "end_hub":
			self.end = Zone(name, x, y)

		elif key == "hub":
			self.zones[name] = Zone(name, x, y)

		else:
			raise(ParseError(f"Error: Invalid Key: {key}"))

	def parse_me_daddy(self, map):
		with map.open() as map_file:
			raw_lines = map_file.readlines()
			print('raw_lines: ', raw_lines)
			for line in raw_lines:
				cleaned = line.split('#')[0].strip()
				if cleaned:
					if cleaned.startswith("nb_drones"):
						self.nb_drones_seen = True
					if not self.nb_drones_seen:
						raise(ParseError("nb_drones must be the first config"))
					key, value = cleaned.split(":")
					if key.strip() == "nb_drones":
						self.nb_drones = self.is_pos_int(value.strip())
					if "hub" in key:
						self.zones = self.parse_zones(key.strip(), value)
					if key.strip() == "connection":
						self.connections = self.parse_connections()

			return (Graph(start, end, zones, connections), self.nb_drones)
