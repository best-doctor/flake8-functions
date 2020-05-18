import ast

from typing import Union, Tuple

from mr_proper.public_api import is_function_pure


AnyFuncdef = Union[ast.FunctionDef, ast.AsyncFunctionDef]


def check_purity_of_functions(func_def: AnyFuncdef) -> Tuple[int, int, str]:
    if 'pure' in func_def.name.split('_') and not is_function_pure(func_def):
        return (
            func_def.lineno,
            func_def.col_offset,
            f'CFQ003 Function "{func_def.name}" is not pure.',
        )
