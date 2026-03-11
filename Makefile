PYTHON ?= 3.13
CONFIG ?= config.example.yaml

.PHONY: create-venv activate-venv install-deps run-plan run-import

create-venv:
	pipenv --python $(PYTHON)

activate-venv:
	@echo "Run this in your shell:"
	@echo "pipenv shell"

install-deps: create-venv
	pipenv install

run-plan:
	pipenv run python -m aon_import.cli plan -c $(CONFIG)

run-import:
	pipenv run python -m aon_import.cli import -c $(CONFIG)
