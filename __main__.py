import sys
from pathlib import Path

from parser import ParseError, Parser
from simulation import Simulation


def main() -> None:

    args = sys.argv[1:]

    file_args = [arg for arg in args]
    if len(file_args) != 1:
        sys.stderr.write("Usage: python3 __main__.py <map_file>\n")
        sys.exit(1)

    map_path = Path(file_args[0])

    try:
        graph = Parser().parse_map(map_path)
        print(
            f"Graph loaded successfully: {len(graph.zones)} zones, "
            f"{len(graph.connections_lst)} connections, "
            f"{graph.nb_drones} drones"
        )
    except ParseError as e:
        sys.stderr.write(f"Parse error: {e}\n")
        sys.exit(1)
    except FileNotFoundError:
        sys.stderr.write(f"Error: File not found: {map_path}\n")
        sys.exit(1)

    sim = Simulation(graph)
    sim.run()


if __name__ == "__main__":
    main()
