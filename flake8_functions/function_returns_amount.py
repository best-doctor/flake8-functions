import ast
from typing import Tuple, Union

AnyFuncdef = Union[ast.FunctionDef, ast.AsyncFunctionDef]


def get_returns_amount_for(func_def: AnyFuncdef) -> int:
    returns_amount = 0
    control_transfer_nodes = (ast.Return,)

    for body_item in func_def.body:
        for sub_node in ast.walk(body_item):
            if isinstance(sub_node, control_transfer_nodes):
                returns_amount += 1

    return returns_amount


def get_returns_amount_error(func_def: AnyFuncdef, max_returns_amount: int) -> Tuple[int, int, str]:
    returns_amount = get_returns_amount_for(func_def)
    if returns_amount > max_returns_amount:
        return (
            func_def.lineno,
            func_def.col_offset,
            f'CFQ004 Function "{func_def.name}" has {returns_amount} returns'
            f' that exceeds max allowed {max_returns_amount}',
        )
