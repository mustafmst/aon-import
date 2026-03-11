PYTHON ?= python3
VENV ?= .venv
CONFIG ?= config.example.yaml
BIN := $(VENV)/bin

.PHONY: create-venv activate-venv install-deps run-plan run-import

create-venv:
	$(PYTHON) -m venv $(VENV)

activate-venv:
	@echo "Run this in your shell:"
	@echo "source $(VENV)/bin/activate"

install-deps: create-venv
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -e .

run-plan:
	$(BIN)/aon-import plan -c $(CONFIG)

run-import:
	$(BIN)/aon-import import -c $(CONFIG)
