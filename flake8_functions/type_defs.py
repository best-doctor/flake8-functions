import ast
from typing import TypeAlias

AnyFuncdef: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef
FunctionError: TypeAlias = tuple[int, int, str]
