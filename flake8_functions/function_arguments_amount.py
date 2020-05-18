import ast
from typing import Tuple, Union

AnyFuncdef = Union[ast.FunctionDef, ast.AsyncFunctionDef]


def get_arguments_amount_for(func_def: AnyFuncdef) -> int:
    arguments_amount = 0
    args = func_def.args
    arguments_amount += len(args.args) + len(args.kwonlyargs)
    if args.vararg:
        arguments_amount += 1
    if args.kwarg:
        arguments_amount += 1
    return arguments_amount


def get_arguments_amount_error(func_def: AnyFuncdef, max_parameters_amount: int) -> Tuple[int, int, str]:
    arguments_amount = get_arguments_amount_for(func_def)
    if arguments_amount > max_parameters_amount:
        return (
            func_def.lineno,
            func_def.col_offset,
            f'CFQ002 Function "{func_def.name}" has {arguments_amount} arguments'
            f' that exceeds max allowed {max_parameters_amount}',
        )
