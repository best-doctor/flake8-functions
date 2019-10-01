check:
	flake8 .
	mypy .
	python -m pytest --cov=flake8_functions --cov-report=xml
