import pytest


@pytest.mark.parametrize(
    'first_parameter',
    [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
    ]
)
def function_with_decorator(first_parameter: int):
    first_parameter = (
        first_parameter +
        first_parameter
    )

    return first_parameter
