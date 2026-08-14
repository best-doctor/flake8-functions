import ast

from flake8_functions.type_defs import AnyFuncdef, FunctionError


def _is_docstring(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def get_function_start_row(func_def: AnyFuncdef) -> int:
    first_meaningful_expression_index = 0
    if _is_docstring(func_def.body[0]) and len(func_def.body) > 1:
        first_meaningful_expression_index = 1
    return func_def.body[first_meaningful_expression_index].lineno


def get_function_last_row(func_def: AnyFuncdef) -> int:
    function_last_line = 0
    for statement in ast.walk(func_def):
        lineno = getattr(statement, 'lineno', None)
        if lineno is not None:
            function_last_line = max(lineno, function_last_line)

    return function_last_line


def get_length_errors(func_def: AnyFuncdef, max_function_length: int) -> FunctionError | None:
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
    return None
