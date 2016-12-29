
venv:
	pip install --upgrade virtualenv
	virtualenv --python=python3 venv

install: venv
	. venv/bin/activate; \
	pip install -e .

unit-test:
	. venv/bin/activate; \
	python -m unittest discover tests/

build:
	rm -rf build; rm -rf dist; \
	. venv/bin/activate; \
	python setup.py sdist bdist_wheel

upload:
	. venv/bin/activate; \
	twine upload dist/*

upload-test:
	. venv/bin/activate; \
	twine upload -r pypitest dist/*
