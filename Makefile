.PHONY: install
install:
	pip install -U -r requirements.txt

.PHONY: test
test:
	pytest

.PHONY: format
format:
	autoflake -i --remove-all-unused-imports --ignore-init-module-imports --expand-star-imports --exclude venv -r .
	isort .
	black .

	docformatter -i ezyquant_execute/context.py

.PHONY: venv
venv:
	python -m venv venv
