
import ast
from typing import Tuple, Union

AnyFuncdef = Union[ast.FunctionDef, ast.AsyncFunctionDef]


def get_function_start_row(func_def: AnyFuncdef) -> int:
    first_meaningful_expression_index = 0
    if (
        isinstance(func_def.body[0], ast.Expr)
        and isinstance(func_def.body[0].value, ast.Str)
        and len(func_def.body) > 1
    ):  # First expression is docstring - we ignore it
        first_meaningful_expression_index = 1
    return func_def.body[first_meaningful_expression_index].lineno


def get_function_last_row(func_def: AnyFuncdef) -> int:
    function_last_line = 0
    for statement in ast.walk(func_def):
        if hasattr(statement, 'lineno'):
            function_last_line = max(statement.lineno, function_last_line)

    return function_last_line


def get_length_errors(func_def: AnyFuncdef, max_function_length: int) -> Tuple[int, int, str]:
    function_start_row = get_function_start_row(func_def)
    function_last_row = get_function_last_row(func_def)
    function_length = function_last_row - function_start_row + 1
    if function_length > max_function_length:
        return (
            func_def.lineno,
            func_def.col_offset,
            f'CFQ001 Function {func_def.name} has length {function_length}'
            f' that exceeds max allowed length {max_function_length}',
        )
