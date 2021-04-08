# flake8-functions

[![Build Status](https://travis-ci.org/best-doctor/flake8-functions.svg?branch=master)](https://travis-ci.org/best-doctor/flake8-functions)
[![Maintainability](https://api.codeclimate.com/v1/badges/4cdbd67833752665ee79/maintainability)](https://codeclimate.com/github/best-doctor/flake8-functions/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/4cdbd67833752665ee79/test_coverage)](https://codeclimate.com/github/best-doctor/flake8-functions/test_coverage)
[![PyPI version](https://badge.fury.io/py/flake8-functions.svg?)](https://badge.fury.io/py/flake8-functions)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flake8-functions)

An extension for flake8 to report on issues with functions.

We believe code readability is very important for a team that consists of
more than one person. One of the issues we've encountered is functions
that are more that two screens long.

The validator checks for:

* CFQ001 - function length (default max length is 100)
* CFQ002 - function arguments number (default max arguments amount is 6)
* CFQ003 - function is not pure.
* CFQ004 - function returns number (default max returns amount is 3)

## Installation

```terminal
pip install flake8-functions
```

## Example

```python
def some_long_function(
    first_parameter: int,
    second_parameter: int,
    third_parameter: int,
):
    first_parameter = (
        first_parameter +
        second_parameter +
        third_parameter
    )

    first_parameter = (
        first_parameter +
        second_parameter +
        third_parameter
    )

    first_parameter = (
        first_parameter +
        second_parameter +
        third_parameter
    )

    first_parameter = (
        first_parameter +
        second_parameter +
        third_parameter
    )

    return first_parameter
```

Usage:

```terminal
$ flake8 --max-function-length=20 test.py
test.py:1:0: CFQ001 "some_long_function" function has length 25
that exceeds max allowed length 20
```

## Error codes

| Error code |                     Description                                                                    |
|:----------:|:--------------------------------------------------------------------------------------------------:|
|   CFQ001   | Function "some_function" has length %function_length% that exceeds max allowed length %max_length% |
|   CFQ002   | Function "some_function" has %args_amount% arguments that exceeds max allowed %max_args_amount%    |
|   CFQ003   | Function "some_function" is not pure.                                                              |
|   CFQ004   | Function "some_function" has %returns_amount% returns that exceeds max allowed %max_returns_amount%|

## Code prerequisites

1. Python 3.7+;

## Contributing

We would love you to contribute to our project. It's simple:

1. Create an issue with bug you found or proposal you have.
   Wait for approve from maintainer.
1. Create a pull request. Make sure all checks are green.
1. Fix review comments if any.
1. Be awesome.

Here are useful tips:

* You can run all checks and tests with `make check`.
  Please do it before TravisCI does.
* We use [BestDoctor python styleguide](https://github.com/best-doctor/guides/blob/master/guides/en/python_styleguide.md).
* We respect [Django CoC](https://www.djangoproject.com/conduct/).
  Make soft, not bullshit.
