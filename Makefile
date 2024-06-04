PROJECT_PATH := dnslib

VERSION = $(shell poetry version -s)

all:
	@echo "make develop   - Prepare the project development env"
	@echo "make lint      - Syntax check python with ruff"
	@echo "make format 		- Format project with ruff"
	@echo "make clean 		- Remove files which creates by distutils"
	@exit 0

clean:
	rm -rf dist

lint:
	poetry run ruff check

format:
	poetry run ruff format

develop: clean
	poetry -V
	poetry install
	poetry run pre-commit install
