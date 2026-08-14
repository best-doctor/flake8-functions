import pytest

from flake8_functions.function_length import (
    get_function_last_row,
    get_function_start_row,
    get_length_errors,
)

FUNCTION_WITH_DOCSTRING = '''
def foo(arg):
    """Docstring."""
    return arg
'''

FUNCTION_WITHOUT_DOCSTRING = '''
def foo(arg):
    return arg
'''

DOCSTRING_ONLY_FUNCTION = '''
def foo(arg):
    """Docstring is the only statement."""
'''

ASYNC_FUNCTION_WITH_DOCSTRING = '''
async def foo(arg):
    """Docstring."""
    return arg
'''

DEEPLY_NESTED_FUNCTION = '''
def foo():
    if True:
        if True:
            return 1
'''

ASYNC_FUNCTION_WITH_ASYNC_STATEMENTS = '''
async def foo(source):
    async with source as stream:
        async for item in stream:
            await handle(item)
'''

DECORATED_FUNCTION = '''
@decorator(
    'first',
    'second',
)
def foo():
    return 1
'''


@pytest.mark.parametrize(
    ('source', 'expected_start_row'),
    [
        (FUNCTION_WITH_DOCSTRING, 4),
        (FUNCTION_WITHOUT_DOCSTRING, 3),
        (DOCSTRING_ONLY_FUNCTION, 3),
        (ASYNC_FUNCTION_WITH_DOCSTRING, 4),
    ],
    ids=[
        'docstring-skipped',
        'no-docstring',
        'docstring-is-only-statement',
        'async-docstring-skipped',
    ],
)
def test__get_function_start_row__success_case(source, expected_start_row, parse_funcdef):
    """
    Arrange: functions with a docstring, without one, and with a docstring only
    Act: compute the row of the first meaningful statement
    Assert: the docstring is skipped unless it is the only statement in the body
    """
    func_def = parse_funcdef(source)

    start_row = get_function_start_row(func_def)

    assert start_row == expected_start_row


@pytest.mark.parametrize(
    ('source', 'expected_last_row'),
    [
        (DEEPLY_NESTED_FUNCTION, 5),
        (ASYNC_FUNCTION_WITH_ASYNC_STATEMENTS, 5),
    ],
    ids=['nested-if-statements', 'async-with-and-async-for'],
)
def test__get_function_last_row__counts_deepest_nested_statement(
    source,
    expected_last_row,
    parse_funcdef,
):
    """
    Arrange: functions whose last statement is deeply nested, including async ones
    Act: compute the last row of the function
    Assert: the row of the deepest nested statement is returned
    """
    func_def = parse_funcdef(source)

    last_row = get_function_last_row(func_def)

    assert last_row == expected_last_row


def test__get_function_last_row__decorator_is_ignored(parse_funcdef):
    """
    Arrange: a function under a multiline decorator
    Act: compute the boundaries of the function
    Assert: decorator rows do not contribute to the function length
    """
    func_def = parse_funcdef(DECORATED_FUNCTION)

    function_length = get_function_last_row(func_def) - get_function_start_row(func_def) + 1

    assert function_length == 1


@pytest.mark.parametrize(
    ('max_function_length', 'expected_error'),
    [
        (3, None),
        (2, (2, 0)),
        (0, (2, 0)),
    ],
    ids=['equal-to-limit', 'exceeds-limit-by-one', 'zero-limit'],
)
def test__get_length_errors__respects_max_function_length(
    max_function_length,
    expected_error,
    parse_funcdef,
):
    """
    Arrange: a function that is three meaningful rows long
    Act: check it against different function length limits
    Assert: an error carrying the function position is returned only above the limit
    """
    func_def = parse_funcdef(DEEPLY_NESTED_FUNCTION)

    error = get_length_errors(func_def, max_function_length=max_function_length)

    assert (error[:2] if error else None) == expected_error


@pytest.mark.parametrize(
    'source',
    [FUNCTION_WITH_DOCSTRING, ASYNC_FUNCTION_WITH_DOCSTRING],
    ids=['sync-function', 'async-function'],
)
def test__get_length_errors__docstring_is_not_counted(source, parse_funcdef):
    """
    Arrange: sync and async functions with a docstring and a single meaningful row
    Act: check them against a one row length limit
    Assert: no error is reported, the docstring does not add to the length
    """
    func_def = parse_funcdef(source)

    error = get_length_errors(func_def, max_function_length=1)

    assert error is None


def test__get_length_errors__error_message(parse_funcdef):
    """
    Arrange: a function exceeding the length limit
    Act: get the reported error
    Assert: the message contains CFQ001, the function name, its length and the limit
    """
    func_def = parse_funcdef(DEEPLY_NESTED_FUNCTION)

    error = get_length_errors(func_def, max_function_length=1)

    assert error is not None
    assert error[2] == 'CFQ001 Function foo has length 3 that exceeds max allowed length 1'
