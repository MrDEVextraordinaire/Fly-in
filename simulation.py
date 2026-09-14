from models import Drone, Graph


class Simulation:
    """Represents the simulation of drones moving through a graph of zones."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def run(self) -> None:
        """Run a single drone simulation from start to end."""
        # Initialize drones at the start zone
        # keep moving the drone and check state
        # mark it arrived if it reaches the end zone
        path = self.graph.pathfinder(save_path=True)
        if not isinstance(path, list) or not path:
            return

        drones = [Drone(drone_id=i + 1, path=path) for i in range(self.graph.nb_drones)]

        self.graph.start.current_drones = [drone.drone_id for drone in drones]

        while not all(drone.has_arrived for drone in drones):
            # if all drones have not arrived yet continue simulation
            # check the farthest ahead drone by checking the steps taken and check
            # if he can move to the next zone if not then check the next drone and so on
            # until all drones have arrived at the end zone
            turn_moves = []

            for conn in self.graph.connections_lst:
                conn.current_drones.clear()

            active_drones = [drone for drone in drones if not drone.has_arrived]
            active_drones.sort(key=lambda d: d.steps_taken, reverse=True)

            for drone in active_drones:
                next_zone = drone.next_zone
                current_zone = drone.current_zone

                # find the connection between current_zone and next_zone
                conn = next(
                    c
                    for n, c in self.graph.get_neighbors(current_zone)
                    if n == next_zone
                )

                if (
                    next_zone
                    and len(next_zone.current_drones) < next_zone.max_drones
                    and len(conn.current_drones) < conn.max_link_capacity
                ):
                    current_zone.current_drones.remove(drone.drone_id)
                    next_zone.current_drones.append(drone.drone_id)
                    drone.steps_taken += 1

                    conn.current_drones.append(drone.drone_id)

                    turn_moves.append(f"D{drone.drone_id}-{drone.current_zone.name}")
            if turn_moves:
                print(" ".join(turn_moves))
