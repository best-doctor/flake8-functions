import ast

import pytest

from flake8_functions.checker import FunctionChecker


@pytest.mark.parametrize(
    'filename',
    [
        'file_with_defs.py',
        'file_with_async_defs.py',
        'file_with_mixed_defs.py',
    ],
    ids=['sync-defs', 'async-defs', 'mixed-defs'],
)
@pytest.mark.parametrize(
    ('max_function_length', 'expected_errors_count'),
    [
        (25, 0),
        (24, 1),
        (23, 1),
        (6, 1),
        (5, 2),
        (4, 2),
        (0, 2),
    ],
    ids=[
        'limit-above-long-function',
        'limit-equal-to-long-function',
        'limit-below-long-function',
        'limit-above-short-function',
        'limit-equal-to-short-function',
        'limit-below-short-function',
        'zero-limit',
    ],
)
def test__checker__reports_too_long_functions(
    filename,
    max_function_length,
    expected_errors_count,
    run_checker_for_test_file,
):
    """
    Arrange: files with plain, async and mixed function definitions
    Act: run the checker with different function length limits
    Assert: the error count does not depend on the def kind and grows as the limit drops
    """
    errors = run_checker_for_test_file(
        filename=filename,
        max_function_length=max_function_length,
    )

    assert len(errors) == expected_errors_count


def test__checker__counts_deeply_nested_last_statement(run_checker_for_test_file):
    """
    Arrange: a file with deeply nested conditions inside a function
    Act: run the checker with a length limit of 4
    Assert: nested rows count towards the length and a single error is reported
    """
    errors = run_checker_for_test_file(
        filename='file_with_deep_nested.py',
        max_function_length=4,
    )

    assert len(errors) == 1


def test__checker__ignores_decorator_length(run_checker_for_test_file):
    """
    Arrange: a file with a function under a long multiline decorator
    Act: run the checker with a length limit of 6
    Assert: decorator rows are not counted and no error is reported
    """
    errors = run_checker_for_test_file(
        filename='file_with_long_decorator.py',
        max_function_length=6,
    )

    assert not errors


def test__checker__processes_function_with_pass_only(run_checker_for_test_file):
    """
    Arrange: a file with sync and async functions consisting of a single pass
    Act: run the checker with a length limit of 1 and zero allowed returns
    Assert: a single-pass function is not reported as a violation
    """
    errors = run_checker_for_test_file(
        filename='file_pass_function.py',
        max_function_length=1,
        max_returns_amount=0,
    )

    assert not errors


def test__checker__reports_too_many_arguments(run_checker_for_test_file):
    """
    Arrange: a file with three functions, each taking more than three arguments
    Act: run the checker with a limit of three arguments
    Assert: an error is reported for each of the three functions
    """
    errors = run_checker_for_test_file(
        filename='file_with_lots_of_arguments.py',
        max_parameters_amount=3,
    )

    assert len(errors) == 3


@pytest.mark.parametrize(
    ('max_function_length', 'expected_errors_count'),
    [
        (4, 0),
        (3, 1),
    ],
    ids=['within-limit', 'exceeds-limit'],
)
def test__checker__docstring_is_not_part_of_function_length(
    max_function_length,
    expected_errors_count,
    run_checker_for_test_file,
):
    """
    Arrange: a file with a function carrying a long multiline docstring
    Act: run the checker with length limits of 4 and 3
    Assert: docstring rows do not add to the function length
    """
    errors = run_checker_for_test_file(
        filename='file_with_docstring.py',
        max_function_length=max_function_length,
    )

    assert len(errors) == expected_errors_count


@pytest.mark.parametrize(
    ('filename', 'expected_errors_count'),
    [
        ('file_pure_function.py', 0),
        ('file_not_pure_function.py', 1),
    ],
    ids=['pure-function', 'impure-function'],
)
def test__checker__reports_impure_functions(
    filename,
    expected_errors_count,
    run_checker_for_test_file,
):
    """
    Arrange: files with a pure and an impure function, both named with 'pure'
    Act: run the checker with default settings
    Assert: only the impure function is reported
    """
    errors = run_checker_for_test_file(filename=filename)

    assert len(errors) == expected_errors_count


@pytest.mark.parametrize(
    ('max_returns_amount', 'expected_errors_count'),
    [
        (10, 0),
        (5, 0),
        (4, 1),
        (2, 1),
        (0, 1),
    ],
    ids=[
        'limit-far-above',
        'limit-equal-to-returns',
        'limit-below-returns',
        'low-limit',
        'zero-limit',
    ],
)
def test__checker__reports_too_many_returns(
    max_returns_amount,
    expected_errors_count,
    run_checker_for_test_file,
):
    """
    Arrange: a file with a function containing five returns
    Act: run the checker with different return count limits
    Assert: an error is reported only when the return count is above the limit
    """
    errors = run_checker_for_test_file(
        filename='file_with_lots_of_returns.py',
        max_returns_amount=max_returns_amount,
    )

    assert len(errors) == expected_errors_count


@pytest.mark.parametrize(
    ('max_returns_amount', 'expected_errors_count'),
    [
        (10, 0),
        (5, 0),
        (4, 1),
        (1, 1),
        (0, 5),
    ],
    ids=[
        'limit-far-above',
        'limit-equal-to-returns',
        'limit-below-returns',
        'low-limit',
        'zero-limit-hits-nested-defs-too',
    ],
)
def test__checker__counts_returns_of_nested_defs(
    max_returns_amount,
    expected_errors_count,
    run_checker_for_test_file,
):
    """
    Arrange: a file with a function wrapping four nested functions with returns
    Act: run the checker with different return count limits
    Assert: nested returns count towards the outer function, and the nested
        functions are checked on their own as well
    """
    errors = run_checker_for_test_file(
        filename='file_with_nested_defs.py',
        max_returns_amount=max_returns_amount,
    )

    assert len(errors) == expected_errors_count


def test__checker__yields_flake8_compatible_error_tuples(run_checker_for_test_file):
    """
    Arrange: a file with two functions exceeding the length limit
    Act: run the checker and unpack the structure of its errors
    Assert: every error is a (row, column, message, checker class) tuple
    """
    errors = run_checker_for_test_file(filename='file_with_defs.py', max_function_length=0)

    assert len(errors) == 2
    assert all(isinstance(lineno, int) for lineno, _, _, _ in errors)
    assert all(isinstance(col_offset, int) for _, col_offset, _, _ in errors)
    assert all(message.startswith('CFQ') for _, _, message, _ in errors)
    assert all(checker_class is FunctionChecker for _, _, _, checker_class in errors)


@pytest.mark.parametrize(
    ('source', 'expected_codes'),
    [
        ('async def foo(a, b, c, d):\n    return a\n', ['CFQ002']),
        ('async def pure_foo(qs):\n    print(qs)\n', ['CFQ003']),
        ('async def foo(a):\n    if a:\n        return 1\n    return 0\n', ['CFQ004']),
        (
            'class Service:\n'
            '    async def method(self, a, b, c, d):\n'
            '        return a\n',
            ['CFQ002'],
        ),
        (
            'def outer():\n'
            '    async def nested(a, b, c, d):\n'
            '        return a\n'
            '    return nested\n',
            ['CFQ004', 'CFQ002'],
        ),
    ],
    ids=[
        'async-too-many-arguments',
        'async-impure-function',
        'async-too-many-returns',
        'async-method-in-class',
        'async-def-nested-in-sync-def',
    ],
)
def test__checker__reports_async_functions(source, expected_codes):
    """
    Arrange: async functions at module level, in a class, and nested in a sync def
    Act: run the checker with limits low enough to be violated
    Assert: async definitions yield exactly the same errors plain ones would
    """
    checker = FunctionChecker(tree=ast.parse(source), filename='async.py')
    checker.max_parameters_amount = 3
    checker.max_returns_amount = 1

    codes = [message.split()[0] for _, _, message, _ in checker.run()]

    assert codes == expected_codes


def test__checker__reports_nothing_for_module_without_functions():
    """
    Arrange: a module without any function definitions
    Act: run the checker
    Assert: no errors are reported
    """
    checker = FunctionChecker(tree=ast.parse('x = 1\n'), filename='empty.py')

    errors = list(checker.run())

    assert not errors
