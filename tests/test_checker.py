import pytest
from conftest import run_validator_for_test_file


@pytest.mark.parametrize(
    'filename',
    [
        'file_with_defs.py',
        'file_with_async_defs.py',
        'file_with_mixed_defs.py',
    ],
)
@pytest.mark.parametrize(
    'max_function_length, errors_count',
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
        'Max length is higher than long function length - 0 errors',
        'Max length is equal to long function length - 1 error',
        'Max length is 1 lower than long function length - 1 error',
        'Max length is 1 higher than short function length - 1 error',
        'Max length is equal to short function length - 2 errors',
        'Max length is 1 lower than short function length - 2 errors',
        'Max length is zero - 2 errors',
    ],
)
def test_max_function_length(filename, max_function_length, errors_count):
    errors = run_validator_for_test_file(
        filename=filename,
        max_function_length=max_function_length,
    )

    assert len(errors) == errors_count


def test_nested_last_statement():
    errors = run_validator_for_test_file(
        filename='file_with_deep_nested.py',
        max_function_length=4,
    )

    assert len(errors) == 1


def test_decorator_is_ignored():
    errors = run_validator_for_test_file(
        filename='file_with_long_decorator.py',
        max_function_length=6,
    )

    assert len(errors) == 0


def test_pass_function_is_processed():
    errors = run_validator_for_test_file(
        filename='file_pass_function.py',
        max_function_length=1,
        max_returns_amount=0,
    )

    assert len(errors) == 0


def test_shows_error_for_too_much_arguments():
    errors = run_validator_for_test_file(
        filename='file_with_lots_of_arguments.py',
        max_parameters_amount=3,
    )

    assert len(errors) == 3


@pytest.mark.parametrize(
    'max_function_length, expected_errors_count',
    [
        (4, 0),
        (3, 1),
    ],
)
def test_dosctrings_are_not_part_of_function_length(max_function_length, expected_errors_count):
    errors = run_validator_for_test_file(
        filename='file_with_docstring.py',
        max_function_length=max_function_length,
    )

    assert len(errors) == expected_errors_count


def test_function_purity():
    errors = run_validator_for_test_file(
        filename='file_pure_function.py',
    )

    assert len(errors) == 0


def test_not_function_purity():
    errors = run_validator_for_test_file(
        filename='file_not_pure_function.py',
    )

    assert len(errors) == 1


@pytest.mark.parametrize(
    'max_returns_amount, expected_errors_count',
    [
        (10, 0),
        (5, 0),
        (4, 1),
        (2, 1),
        (0, 1),
    ],
)
def test_too_much_returns(max_returns_amount, expected_errors_count):
    errors = run_validator_for_test_file(
        filename='file_with_lots_of_returns.py',
        max_returns_amount=max_returns_amount,
    )

    assert len(errors) == expected_errors_count


@pytest.mark.parametrize(
    'max_returns_amount, expected_errors_count',
    [
        (10, 0),
        (5, 0),
        (4, 1),
        (1, 1),
        (0, 5),  # because nested functions have errors
    ],
)
def test_nested_defs_with_returns(max_returns_amount, expected_errors_count):
    errors = run_validator_for_test_file(
        filename='file_with_nested_defs.py',
        max_returns_amount=max_returns_amount,
    )

    assert len(errors) == expected_errors_count
