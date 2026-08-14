import argparse

import pytest

from flake8_functions.checker import FunctionChecker


class OptionParserStub:
    """Minimal stand-in for the flake8 OptionManager, used to check add_options."""

    def __init__(self):
        self.options = []

    def add_option(self, name, **kwargs):
        self.options.append((name, kwargs))


@pytest.fixture()
def restore_checker_defaults():
    """Restore the checker class limits after a test that mutates them globally."""
    saved = (
        FunctionChecker.max_function_length,
        FunctionChecker.max_parameters_amount,
        FunctionChecker.max_returns_amount,
    )

    yield

    (
        FunctionChecker.max_function_length,
        FunctionChecker.max_parameters_amount,
        FunctionChecker.max_returns_amount,
    ) = saved


def test__add_options__registers_every_configurable_limit():
    """
    Arrange: a stub of the flake8 option parser
    Act: register the checker options
    Assert: all three limits are registered and read from the config
    """
    parser = OptionParserStub()

    FunctionChecker.add_options(parser)

    assert [name for name, _ in parser.options] == [
        '--max-function-length',
        '--max-parameters-amount',
        '--max-returns-amount',
    ]
    assert all(kwargs['parse_from_config'] for _, kwargs in parser.options)


def test__add_options__defaults_match_class_attributes():
    """
    Arrange: a stub of the flake8 option parser
    Act: register the checker options
    Assert: option defaults are taken from the checker class constants
    """
    parser = OptionParserStub()

    FunctionChecker.add_options(parser)

    assert [kwargs['default'] for _, kwargs in parser.options] == [
        FunctionChecker.DEFAULT_MAX_FUNCTION_LENGTH,
        FunctionChecker.DEFAULT_MAX_FUNCTION_ARGUMENTS_AMOUNT,
        FunctionChecker.DEFAULT_MAX_FUNCTION_RETURNS_AMOUNT,
    ]


@pytest.mark.usefixtures('restore_checker_defaults')
def test__parse_options__overrides_class_defaults():
    """
    Arrange: a flake8 options namespace differing from the defaults
    Act: apply it via parse_options
    Assert: the checker starts using the provided limits
    """
    options = argparse.Namespace(
        max_function_length='42',
        max_parameters_amount='7',
        max_returns_amount='2',
    )

    FunctionChecker.parse_options(options)

    assert FunctionChecker.max_function_length == 42
    assert FunctionChecker.max_parameters_amount == 7
    assert FunctionChecker.max_returns_amount == 2


@pytest.mark.usefixtures('restore_checker_defaults')
def test__parse_options__coerces_string_values_to_int():
    """
    Arrange: a namespace whose limits come from a config file as strings
    Act: apply it via parse_options
    Assert: the limits are stored as ints, so comparisons in the checks work
    """
    options = argparse.Namespace(
        max_function_length='10',
        max_parameters_amount='5',
        max_returns_amount='1',
    )

    FunctionChecker.parse_options(options)

    assert isinstance(FunctionChecker.max_function_length, int)
    assert isinstance(FunctionChecker.max_parameters_amount, int)
    assert isinstance(FunctionChecker.max_returns_amount, int)
