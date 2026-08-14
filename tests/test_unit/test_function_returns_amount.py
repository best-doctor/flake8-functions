import pytest

from flake8_functions.function_returns_amount import (
    get_returns_amount_error,
    get_returns_amount_for,
)

NO_RETURNS = '''
def foo(param):
    print(param)
'''

SEVERAL_RETURNS = '''
def foo(param):
    if param == 1:
        return 1
    if param == 2:
        return 2
    return 0
'''

RETURNS_INSIDE_NESTED_DEF = '''
def foo():
    def wrapper():
        return 1

    return wrapper
'''

ASYNC_SEVERAL_RETURNS = '''
async def foo(param):
    if param == 1:
        return 1
    if param == 2:
        return 2
    return 0
'''


@pytest.mark.parametrize(
    ('source', 'expected_amount'),
    [
        (NO_RETURNS, 0),
        (SEVERAL_RETURNS, 3),
        (RETURNS_INSIDE_NESTED_DEF, 2),
        (ASYNC_SEVERAL_RETURNS, 3),
    ],
    ids=[
        'no-returns',
        'several-returns',
        'nested-def-returns-are-counted',
        'async-function',
    ],
)
def test__get_returns_amount_for__success_case(source, expected_amount, parse_funcdef):
    """
    Arrange: functions without returns, with several returns, and with a nested def
    Act: count the returns of the function
    Assert: returns of nested functions are also counted towards the outer one
    """
    func_def = parse_funcdef(source)

    returns_amount = get_returns_amount_for(func_def)

    assert returns_amount == expected_amount


@pytest.mark.parametrize(
    ('max_returns_amount', 'has_error'),
    [
        (4, False),
        (3, False),
        (2, True),
        (0, True),
    ],
    ids=['above-limit', 'equal-to-limit', 'exceeds-limit', 'zero-limit'],
)
def test__get_returns_amount_error__respects_max_returns_amount(
    max_returns_amount,
    has_error,
    parse_funcdef,
):
    """
    Arrange: a function with three returns
    Act: check it against different return limits
    Assert: an error is returned only when the return count is above the limit
    """
    func_def = parse_funcdef(SEVERAL_RETURNS)

    error = get_returns_amount_error(func_def, max_returns_amount=max_returns_amount)

    assert (error is not None) is has_error


@pytest.mark.parametrize(
    'source',
    [SEVERAL_RETURNS, ASYNC_SEVERAL_RETURNS],
    ids=['sync-function', 'async-function'],
)
def test__get_returns_amount_error__error_message(source, parse_funcdef):
    """
    Arrange: sync and async functions with three returns and a limit of one
    Act: get the reported error
    Assert: the message contains CFQ004, the function name, the count and the limit
    """
    func_def = parse_funcdef(source)

    error = get_returns_amount_error(func_def, max_returns_amount=1)

    assert error is not None
    assert error[2] == 'CFQ004 Function "foo" has 3 returns that exceeds max allowed 1'
