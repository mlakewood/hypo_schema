
venv:
	pip install --upgrade virtualenv
	virtualenv --python=python3 venv

install: venv
	. venv/bin/activate; \
	pip install -e .

unit-test:
	. venv/bin/activate; \
	python -m unittest discover tests/
