import ast
from typing import Generator, Tuple, List, Dict, Any, Union

from flake8_functions import __version__ as version


class FunctionChecker:
    name = 'flake8-functions'
    version = version

    DEFAULT_MAX_FUNCTION_LENGTH = 100

    max_function_length = DEFAULT_MAX_FUNCTION_LENGTH

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

    @classmethod
    def add_options(cls, parser) -> None:
        parser.add_option(
            '--max-function-length',
            type=int,
            default=cls.DEFAULT_MAX_FUNCTION_LENGTH,
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options) -> None:
        cls.max_function_length = int(options.max_function_length)

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
