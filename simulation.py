from models import Drone, Graph, Visualizer


class Simulation:
    """Represents the simulation of drones moving through a graph of zones."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.visualizer = Visualizer()

    def run(self) -> None:
        """Run a single drone simulation from start to end."""
        path = self.graph.pathfinder(weighted=True)
        if not path:
            return

        drones = [
            Drone(drone_id=i + 1, path=path)
            for i in range(self.graph.nb_drones)
        ]

        self.graph.start.current_drones = [drone.drone_id for drone in drones]

        while not all(drone.has_arrived for drone in drones):
            turn_moves: list[str] = []

            for conn in self.graph.connections_lst:
                conn.current_drones.clear()

            active_drones = [
                drone for drone in drones if not drone.has_arrived
            ]
            active_drones.sort(key=lambda d: d.steps_taken, reverse=True)

            for drone in active_drones:
                next_zone = drone.next_zone
                current_zone = drone.current_zone

                if drone.travelling is not None and next_zone is not None:
                    destination = next_zone
                    destination.current_drones.append(drone.drone_id)
                    drone.steps_taken += 1
                    drone.travelling = None
                    colored_zone = self.visualizer.colorize(
                        destination.name, destination.color
                    )
                    turn_moves.append(f"D{drone.drone_id}-{colored_zone}")

                else:
                    conn = next(
                        c
                        for n, c in self.graph.get_neighbors(current_zone)
                        if n == next_zone
                    )
                    if (
                        next_zone
                        and len(next_zone.current_drones)
                        < next_zone.max_drones
                        and len(conn.current_drones)
                        < conn.max_link_capacity
                    ):
                        current_zone.current_drones.remove(drone.drone_id)
                        conn.current_drones.append(drone.drone_id)
                        if next_zone._type == "restricted":
                            drone.travelling = conn
                            conn_name = f"{current_zone.name}-{next_zone.name}"
                            turn_moves.append(f"D{drone.drone_id}-{conn_name}")

                        else:
                            next_zone.current_drones.append(drone.drone_id)
                            drone.steps_taken += 1
                            colored_zone = self.visualizer.colorize(
                                next_zone.name, next_zone.color
                            )
                            turn_moves.append(
                                f"D{drone.drone_id}-{colored_zone}"
                            )
            if turn_moves:
                print(" ".join(turn_moves))
