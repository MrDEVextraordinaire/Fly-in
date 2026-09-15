NAME = flyin
PYTHON = python3
ENTRY = __main__.py
MAP = maps/easy/01_linear_path.txt

all: run

install:
	pip install -r requirements.txt


run:
ifndef file
	$(error file is undefined. Use 'make run file=<filepath>')
endif
	$(PYTHON) $(ENTRY) $(file)


debug:
ifndef file
	$(error file is undefined. Use 'make debug file=<filepath>')
endif
	$(PYTHON) -m pdb $(ENTRY) $(file)

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache

fclean: clean

re: fclean all

.PHONY: all install run lint clean fclean re debug
