import ast
from typing import Generator, Tuple, List, Dict, Any, Union

from flake8_functions import __version__ as version


AnyFuncdef = Union[ast.FunctionDef, ast.AsyncFunctionDef]


class FunctionChecker:
    name = 'flake8-functions'
    version = version

    DEFAULT_MAX_FUNCTION_LENGTH = 100
    DEFAULT_MAX_FUNCTION_ARGUMENTS_AMOUNT = 6

    max_function_length = DEFAULT_MAX_FUNCTION_LENGTH
    max_parameters_amount = DEFAULT_MAX_FUNCTION_ARGUMENTS_AMOUNT

    def __init__(self, tree, filename: str):
        self.filename = filename
        self.tree = tree

    @staticmethod
    def _get_function_length(
        func_def: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> Dict[str, Any]:
        function_start_row = func_def.body[0].lineno  # We ignore decorators and signature
        function_last_statement = func_def.body[-1]
        while hasattr(function_last_statement, 'body'):
            function_last_statement = getattr(function_last_statement, 'body')[-1]
        func_def_info = {
            'name': func_def.name,
            'lineno': func_def.lineno,
            'col_offset': func_def.col_offset,
            'length': function_last_statement.lineno - function_start_row + 1,
        }
        return func_def_info

    @staticmethod
    def _get_length_errors(
        func_def_info: Dict[str, Any],
        max_function_length: int,
    ) -> List[Tuple[int, int, str]]:
        errors = []
        if func_def_info['length'] > max_function_length:
            errors.append((
                func_def_info['lineno'],
                func_def_info['col_offset'],
                'CFQ001 Function "{0}" has length {1} that exceeds max allowed length {2}'.format(
                    func_def_info['name'],
                    func_def_info['length'],
                    max_function_length,
                ),
            ))
        return errors

    @staticmethod
    def _get_arguments_amount_for(func_def: AnyFuncdef) -> int:
        arguments_amount = 0
        args = func_def.args
        arguments_amount += len(args.args) + len(args.kwonlyargs)
        if args.vararg:
            arguments_amount += 1
        if args.kwarg:
            arguments_amount += 1
        return arguments_amount

    @classmethod
    def _get_arguments_amount_error(cls, func_def: AnyFuncdef, max_parameters_amount: int) -> Tuple[int, int, str]:
        arguments_amount = cls._get_arguments_amount_for(func_def)
        if arguments_amount > max_parameters_amount:
            return (
                func_def.lineno,
                func_def.col_offset,
                f'CFQ002 Function "{func_def.name}" has {arguments_amount} arguments'
                f' that exceeds max allowed {cls.max_parameters_amount}',
            )

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

    @classmethod
    def parse_options(cls, options) -> None:
        cls.max_function_length = int(options.max_function_length)
        cls.max_parameters_amount = int(options.max_parameters_amount)

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        functions = [
            n for n in ast.walk(self.tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        for func_def in functions:
            func_def_info = self._get_function_length(func_def)
            for lineno, col_offset, error_msg in self._get_length_errors(
                func_def_info, self.max_function_length,
            ):
                yield lineno, col_offset, error_msg, type(self)
            error_info = self._get_arguments_amount_error(func_def, self.max_parameters_amount)
            if error_info:
                full_error_info = *error_info, type(self)
                yield full_error_info
