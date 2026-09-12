from pathlib import Path
import sys

from parser import ParseError, Parser


def main() -> None:
    if len(sys.argv) > 1:
        map_path = Path(sys.argv[1])
    else:
        map_path = Path("./maps/easy/01_linear_path.txt")

    try:
        graph, nb_drones = Parser().parse_map(map_path)
        print(f"Graph loaded successfully: {len(graph.zones)} zones, "
              f"{len(graph.connections)} connections, {nb_drones} drones")
    except ParseError as e:
        sys.stderr.write(f"Parse error: {e}\n")
        sys.exit(1)
    except FileNotFoundError:
        sys.stderr.write(f"Error: File not found: {map_path}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
