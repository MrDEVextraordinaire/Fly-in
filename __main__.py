from pathlib import Path


def main():
	map = Path("./maps/easy/01_linear_path.txt")
	parse_obj = Parser()
	graph = parse_obj.parse_me_daddy(map)


main()