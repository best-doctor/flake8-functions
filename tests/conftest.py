import ast
from collections.abc import Callable
from pathlib import Path
from textwrap import dedent

import pytest

from flake8_functions.checker import FunctionChecker
from flake8_functions.type_defs import AnyFuncdef

TEST_FILES_DIR = Path(__file__).parent / 'test_files'

ParseFuncdef = Callable[[str], AnyFuncdef]
RunChecker = Callable[..., list[tuple[int, int, str, type]]]


@pytest.fixture()
def parse_funcdef() -> ParseFuncdef:
    """Return the first function definition found in the given source code."""
    def parse(source: str) -> AnyFuncdef:
        tree = ast.parse(dedent(source))
        return next(
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        )

    return parse


@pytest.fixture()
def run_checker_for_test_file() -> RunChecker:
    """Run FunctionChecker against a file from tests/test_files."""
    def run(
        filename: str,
        max_function_length: int | None = None,
        max_parameters_amount: int | None = None,
        max_returns_amount: int | None = None,
    ) -> list[tuple[int, int, str, type]]:
        tree = ast.parse((TEST_FILES_DIR / filename).read_text())
        checker = FunctionChecker(tree=tree, filename=filename)
        if max_function_length is not None:
            checker.max_function_length = max_function_length
        if max_parameters_amount is not None:
            checker.max_parameters_amount = max_parameters_amount
        if max_returns_amount is not None:
            checker.max_returns_amount = max_returns_amount

        return list(checker.run())

    return run
