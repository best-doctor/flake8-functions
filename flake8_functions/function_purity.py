import ast
import builtins
from typing import TypeVar

from flake8_functions.type_defs import AnyFuncdef, FunctionError

# Purity rules below are vendored from mr-proper[1], which this project used to
# depend on. The upstream package is unmaintained (last release: 2021, no
# Python 3.10+ support declared) and only its `is_function_pure(func_def)` call
# shape is used here, so the port keeps just that path: no cross-file recursive
# checks, no per-error messages, no stdlib-import awareness - none of those
# ever ran under the arguments this project passed.
# [1] https://pypi.org/project/mr-proper/

_FORBIDDEN_CALLS = frozenset({'print', 'open', 'post'})
_FORBIDDEN_ATTRIBUTES = frozenset({
    'objects', 'post', 'count', 'all', 'exists',
    'filter', 'values_list', 'values', 'save',
})
_FORBIDDEN_ARGUMENT_TYPES = frozenset({'QuerySet', 'Model', 'Callable'})
_MUTATING_METHODS = frozenset({
    'append', 'clear', 'extend', 'insert', 'pop',
    'remove', 'reverse', 'sort', 'update',
})
_FORBIDDEN_NAMES = frozenset({'self', 'cls', 'super'})
_BUILTIN_NAMES = frozenset(name for name in dir(builtins) if not name.startswith('_'))

_NodeT = TypeVar('_NodeT', bound=ast.AST)


def _nodes_of_type(func_def: AnyFuncdef, node_type: type[_NodeT]) -> list[_NodeT]:
    return [
        node
        for statement in func_def.body
        for node in ast.walk(statement)
        if isinstance(node, node_type)
    ]


def _nodes_in_body(func_def: AnyFuncdef, node_types: tuple[type[ast.AST], ...]) -> list[ast.AST]:
    nodes: list[ast.AST] = []
    for statement in func_def.body:
        nodes.extend(node for node in ast.walk(statement) if isinstance(node, node_types))
    return nodes


def _references_any_name(node: ast.AST, names: frozenset[str]) -> bool:
    return any(
        candidate.id in names
        for candidate in ast.walk(node)
        if isinstance(candidate, ast.Name)
    )


def _loop_target_names(loop_node: ast.comprehension | ast.For) -> list[str]:
    target = loop_node.target
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, ast.Tuple):
        return [element.id for element in target.elts if isinstance(element, ast.Name)]
    return []


def _local_variable_names(func_def: AnyFuncdef) -> set[str]:
    names: set[str] = set()
    for assign in _nodes_of_type(func_def, ast.Assign):
        for target in assign.targets:
            names.update(node.id for node in ast.walk(target) if isinstance(node, ast.Name))
    for annotated_assign in _nodes_of_type(func_def, ast.AnnAssign):
        if isinstance(annotated_assign.target, ast.Name):
            names.add(annotated_assign.target.id)
    loop_nodes: list[ast.comprehension | ast.For] = [
        *_nodes_of_type(func_def, ast.comprehension),
        *_nodes_of_type(func_def, ast.For),
    ]
    for loop_node in loop_nodes:
        names.update(_loop_target_names(loop_node))
    names.update(
        handler.name
        for handler in _nodes_of_type(func_def, ast.ExceptHandler)
        if handler.name
    )
    return names


def _calls_forbidden_names(func_def: AnyFuncdef) -> bool:
    for call in _nodes_of_type(func_def, ast.Call):
        if isinstance(call.func, ast.Name) and call.func.id in _FORBIDDEN_CALLS:
            return True
    for attribute in _nodes_of_type(func_def, ast.Attribute):
        if attribute.attr in _FORBIDDEN_ATTRIBUTES:
            return True
    return False


def _uses_external_names(func_def: AnyFuncdef) -> bool:
    referenced_names = {node.id for node in _nodes_of_type(func_def, ast.Name)}
    argument_names = {argument.arg for argument in func_def.args.args}
    called_names = {
        call.func.id
        for call in _nodes_of_type(func_def, ast.Call)
        if isinstance(call.func, ast.Name)
    }
    nested_defs: list[AnyFuncdef] = [
        *_nodes_of_type(func_def, ast.FunctionDef),
        *_nodes_of_type(func_def, ast.AsyncFunctionDef),
    ]
    nested_def_argument_names = {
        argument.arg
        for nested_def in nested_defs
        for argument in nested_def.args.args
    }
    external_names = (
        referenced_names
        - argument_names
        - _local_variable_names(func_def)
        - called_names
        - nested_def_argument_names
        - _BUILTIN_NAMES
    )
    return bool(external_names)


def _has_no_returns(func_def: AnyFuncdef) -> bool:
    return not _nodes_in_body(func_def, (ast.Return, ast.Yield))


def _augassign_mutates_argument(node: ast.AugAssign, argument_names: frozenset[str]) -> bool:
    return _references_any_name(node.target, argument_names)


def _assign_mutates_argument(node: ast.Assign, argument_names: frozenset[str]) -> bool:
    target = node.targets[0]
    if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
        return target.value.id in argument_names
    if isinstance(target, ast.Attribute):
        return _references_any_name(target.value, argument_names)
    return False


def _attribute_call_mutates_argument(node: ast.Attribute, argument_names: frozenset[str]) -> bool:
    return (
        node.attr in _MUTATING_METHODS
        and isinstance(node.value, ast.Name)
        and node.value.id in argument_names
    )


def _mutates_arguments(func_def: AnyFuncdef) -> bool:
    argument_names = frozenset(argument.arg for argument in func_def.args.args)
    return (
        any(
            _augassign_mutates_argument(node, argument_names)
            for node in _nodes_of_type(func_def, ast.AugAssign)
        )
        or any(
            _assign_mutates_argument(node, argument_names)
            for node in _nodes_of_type(func_def, ast.Assign)
        )
        or any(
            _attribute_call_mutates_argument(node, argument_names)
            for node in _nodes_of_type(func_def, ast.Attribute)
        )
    )


def _has_local_imports(func_def: AnyFuncdef) -> bool:
    return bool(_nodes_in_body(func_def, (ast.Import, ast.ImportFrom)))


def _has_forbidden_argument_types(func_def: AnyFuncdef) -> bool:
    for argument in func_def.args.args:
        if argument.annotation is None:
            continue
        for node in ast.walk(argument.annotation):
            if isinstance(node, ast.Name) and node.id in _FORBIDDEN_ARGUMENT_TYPES:
                return True
    return False


def _uses_self_or_class_vars(func_def: AnyFuncdef) -> bool:
    return any(node.id in _FORBIDDEN_NAMES for node in _nodes_of_type(func_def, ast.Name))


def is_function_pure(func_def: AnyFuncdef) -> bool:
    violations = (
        _calls_forbidden_names(func_def),
        _uses_external_names(func_def),
        _has_no_returns(func_def),
        _mutates_arguments(func_def),
        _has_local_imports(func_def),
        _has_forbidden_argument_types(func_def),
        _uses_self_or_class_vars(func_def),
    )
    return not any(violations)


def check_purity_of_functions(func_def: AnyFuncdef) -> FunctionError | None:
    if 'pure' in func_def.name.split('_') and not is_function_pure(func_def):
        return (
            func_def.lineno,
            func_def.col_offset,
            f'CFQ003 Function "{func_def.name}" is not pure.',
        )
    return None
