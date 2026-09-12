class Graph:
    def __init__(self, start, end, zones, connections):
        self.zones = zones
        self.connections = connections
        self.start = start
        self.end = end


class Zone:
    def __init__(
        self, name, x, y, color="white", _type="normal", max_drones=1
    ):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self._type = _type
        self.max_drones = max_drones
