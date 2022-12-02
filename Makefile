.DEFAULT_GOAL:= build
SHELL := /bin/bash
VENV ?= "$(shell poetry env list --full-path | cut -f1 -d " ")/bin/activate"

# Releasing
tag:
	@git tag -a $(version) -m "Release $(version)"
	@git push --follow-tags

# Building
build: check
	@source $(VENV)
	@rm -rf dist || true
	@poetry build

check:
	@source $(VENV)
	@poetry run black --check .
	@poetry run isort --check .
	@poetry run flake8 status_cake_exporter --max-line-length=120 --tee
	@poetry run darglint -s google -m "{path}:{line} -> {msg_id}: {msg}" status_cake_exporteri


# Developing
.PHONY: init
init:
	@poetry install
	@pre-commit install

.PHONY: fix
fix:
	@source $(VENV)
	@poetry run black .
	@poetry run isort .
