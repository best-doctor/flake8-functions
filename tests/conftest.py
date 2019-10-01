import ast
import os

from flake8_functions.checker import FunctionChecker


def run_validator_for_test_file(filename, max_function_length=None):
    test_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'test_files',
        filename,
    )
    with open(test_file_path, 'r') as file_handler:
        raw_content = file_handler.read()
    tree = ast.parse(raw_content)
    checker = FunctionChecker(tree=tree, filename=filename)
    if max_function_length is not None:
        checker.max_function_length = max_function_length

    return list(checker.run())
