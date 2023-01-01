sources = poltergeist tests

.PHONY: test lint check

test:
	pytest -vv tests

lint:
	isort $(sources)
	black $(sources)

check:
	isort --check --diff $(sources)
	black --check --diff $(sources)
	mypy -p poltergeist

type-check:
	python typetests/run.py
