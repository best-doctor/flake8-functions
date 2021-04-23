test:
	python -m pytest

coverage:
	python -m pytest --cov=flake8_functions --cov-report=xml

types:
	mypy .

style:
	flake8 .

readme:
	mdl README.md

requirements:
	safety check -r requirements_dev.txt

check:
	make style
	make types
	make test
	make requirements
