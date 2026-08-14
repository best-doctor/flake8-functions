import argparse
import ast
import functools
from collections.abc import Callable, Generator
from typing import Any

from flake8_functions import __version__ as version
from flake8_functions.function_arguments_amount import get_arguments_amount_error
from flake8_functions.function_length import get_length_errors
from flake8_functions.function_purity import check_purity_of_functions
from flake8_functions.function_returns_amount import get_returns_amount_error
from flake8_functions.type_defs import AnyFuncdef, FunctionError

Validator = Callable[[AnyFuncdef], FunctionError | None]


class FunctionChecker:
    DEFAULT_MAX_FUNCTION_LENGTH = 100
    DEFAULT_MAX_FUNCTION_ARGUMENTS_AMOUNT = 6
    DEFAULT_MAX_FUNCTION_RETURNS_AMOUNT = 3

    name = 'flake8-functions'
    version = version

    max_function_length = DEFAULT_MAX_FUNCTION_LENGTH
    max_parameters_amount = DEFAULT_MAX_FUNCTION_ARGUMENTS_AMOUNT
    max_returns_amount = DEFAULT_MAX_FUNCTION_RETURNS_AMOUNT

    def __init__(self, tree: ast.AST, filename: str) -> None:
        self.filename = filename
        self.tree = tree

    @classmethod
    def add_options(cls, parser: Any) -> None:
        parser.add_option(
            '--max-function-length',
            type=int,
            default=cls.DEFAULT_MAX_FUNCTION_LENGTH,
            parse_from_config=True,
        )
        parser.add_option(
            '--max-parameters-amount',
            type=int,
            default=cls.DEFAULT_MAX_FUNCTION_ARGUMENTS_AMOUNT,
            parse_from_config=True,
        )
        parser.add_option(
            '--max-returns-amount',
            type=int,
            default=cls.DEFAULT_MAX_FUNCTION_RETURNS_AMOUNT,
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        cls.max_function_length = int(options.max_function_length)
        cls.max_parameters_amount = int(options.max_parameters_amount)
        cls.max_returns_amount = int(options.max_returns_amount)

    def run(self) -> Generator[tuple[int, int, str, type], None, None]:
        validators: list[Validator] = [
            functools.partial(
                get_arguments_amount_error,
                max_parameters_amount=self.max_parameters_amount,
            ),
            functools.partial(get_length_errors, max_function_length=self.max_function_length),
            check_purity_of_functions,
            functools.partial(get_returns_amount_error, max_returns_amount=self.max_returns_amount),
        ]
        functions = [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        ]
        for func_def in functions:
            for validator_callable in validators:
                validator_errors = validator_callable(func_def)
                if validator_errors:
                    yield *validator_errors, type(self)
