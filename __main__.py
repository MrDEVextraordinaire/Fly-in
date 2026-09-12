from pathlib import Path

from parser import Parser


def main():
    map = Path("./maps/easy/01_linear_path.txt")
    graph, nb_drones = Parser().parse_map(map)
    print(f"Graph: {graph}, Number of Drones: {nb_drones}")


main()
