check:
	flake8 .
	mypy .
	python -m pytest --cov=flake8_functions --cov-report=xml
	mdl README.md
	safety check -r requirements_dev.txt
