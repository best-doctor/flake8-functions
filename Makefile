.PHONY: install test coverage types style readme requirements lock check

install:
	uv sync --all-groups

test:
	uv run pytest

coverage:
	uv run pytest --cov --cov-report=term-missing --cov-report=xml

types:
	uv run mypy .

style:
	uv run flake8 .

readme:
	npx markdownlint-cli2 "**/*.md"

requirements:
	uv run pip-audit --skip-editable

lock:
	uv lock

check: style types test requirements
