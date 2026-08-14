import pytest

from flake8_functions.function_arguments_amount import (
    get_arguments_amount_error,
    get_arguments_amount_for,
)

NO_ARGUMENTS = 'def foo(): pass'
POSITIONAL_ARGUMENTS = 'def foo(one, two, three): pass'
ARGUMENTS_WITH_DEFAULTS = 'def foo(one, two, three=None, four=None): pass'
VARARG_AND_KWARG = 'def foo(one, two, *args, **kwargs): pass'
KEYWORD_ONLY_ARGUMENTS = 'def foo(one, *, two, three): pass'
POSITION_ONLY_ARGUMENTS = 'def foo(one, two, /, three): pass'
ASYNC_ARGUMENTS = 'async def foo(one, two, /, three, *args, four, **kwargs): pass'


@pytest.mark.parametrize(
    ('source', 'expected_amount'),
    [
        (NO_ARGUMENTS, 0),
        (POSITIONAL_ARGUMENTS, 3),
        (ARGUMENTS_WITH_DEFAULTS, 4),
        (VARARG_AND_KWARG, 4),
        (KEYWORD_ONLY_ARGUMENTS, 3),
        (POSITION_ONLY_ARGUMENTS, 3),
        (ASYNC_ARGUMENTS, 6),
    ],
    ids=[
        'no-arguments',
        'positional',
        'with-defaults',
        'vararg-and-kwarg',
        'keyword-only',
        'position-only',
        'async-function-with-every-kind',
    ],
)
def test__get_arguments_amount_for__counts_every_argument_kind(
    source,
    expected_amount,
    parse_funcdef,
):
    """
    Arrange: functions using every kind of argument, including position-only ones
    Act: count the arguments of the function
    Assert: positional, position-only, keyword-only, *args and **kwargs are counted
    """
    func_def = parse_funcdef(source)

    arguments_amount = get_arguments_amount_for(func_def)

    assert arguments_amount == expected_amount


@pytest.mark.parametrize(
    ('max_parameters_amount', 'has_error'),
    [
        (4, False),
        (3, False),
        (2, True),
        (0, True),
    ],
    ids=['above-limit', 'equal-to-limit', 'exceeds-limit', 'zero-limit'],
)
def test__get_arguments_amount_error__respects_max_parameters_amount(
    max_parameters_amount,
    has_error,
    parse_funcdef,
):
    """
    Arrange: a function with three arguments
    Act: check it against different argument limits
    Assert: an error is returned only when the argument count is above the limit
    """
    func_def = parse_funcdef(POSITIONAL_ARGUMENTS)

    error = get_arguments_amount_error(func_def, max_parameters_amount=max_parameters_amount)

    assert (error is not None) is has_error


def test__get_arguments_amount_error__error_message(parse_funcdef):
    """
    Arrange: a function with three arguments and a limit of one
    Act: get the reported error
    Assert: the message contains CFQ002, the function name, the count and the limit
    """
    func_def = parse_funcdef(POSITIONAL_ARGUMENTS)

    error = get_arguments_amount_error(func_def, max_parameters_amount=1)

    assert error is not None
    assert error[2] == 'CFQ002 Function "foo" has 3 arguments that exceeds max allowed 1'
