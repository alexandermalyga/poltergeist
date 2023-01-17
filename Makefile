sources = poltergeist tests

.PHONY: test lint check

test:
	pytest -vv --cov=poltergeist tests

lint:
	isort $(sources)
	black $(sources)

check:
	isort --check --diff $(sources)
	black --check --diff $(sources)
	mypy -p poltergeist
