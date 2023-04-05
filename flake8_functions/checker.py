import ast
import functools
from typing import Generator, Tuple, Union, List

from flake8_functions import __version__ as version
from flake8_functions.function_purity import check_purity_of_functions
from flake8_functions.function_length import get_length_errors
from flake8_functions.function_arguments_amount import get_arguments_amount_error
from flake8_functions.function_returns_amount import get_returns_amount_error

AnyFuncdef = Union[ast.FunctionDef, ast.AsyncFunctionDef]


class FunctionChecker:
    DEFAULT_MAX_FUNCTION_LENGTH = 100
    DEFAULT_MAX_FUNCTION_ARGUMENTS_AMOUNT = 6
    DEFAULT_MAX_FUNCTION_RETURNS_AMOUNT = 3

    name = 'flake8-functions'
    version = version

    max_function_length = DEFAULT_MAX_FUNCTION_LENGTH
    max_parameters_amount = DEFAULT_MAX_FUNCTION_ARGUMENTS_AMOUNT
    max_returns_amount = DEFAULT_MAX_FUNCTION_RETURNS_AMOUNT

    def __init__(self, tree, filename: str):
        self.filename = filename
        self.tree = tree

    @classmethod
    def add_options(cls, parser) -> None:
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
    def parse_options(cls, options) -> None:
        cls.max_function_length = int(options.max_function_length)
        cls.max_parameters_amount = int(options.max_parameters_amount)
        cls.max_returns_amount = int(options.max_returns_amount)

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        validators: List = [
            functools.partial(get_arguments_amount_error, max_parameters_amount=self.max_parameters_amount),
            functools.partial(get_length_errors, max_function_length=self.max_function_length),
            check_purity_of_functions,
            functools.partial(get_returns_amount_error, max_returns_amount=self.max_returns_amount),
        ]
        functions = [
            n for n in ast.walk(self.tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        for func_def in functions:
            for validator_callable in validators:
                validator_errors: Tuple[int, int, str] = validator_callable(func_def)
                if validator_errors:
                    full_error_info = *validator_errors, type(self)
                    yield full_error_info
