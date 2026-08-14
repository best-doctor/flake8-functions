import pytest

from flake8_functions.function_purity import check_purity_of_functions, is_function_pure

PURE_FUNCTION = '''
def pure_add(number: int) -> int:
    return number + 1
'''

IMPURE_FUNCTION_WITH_PURE_IN_NAME = '''
def not_pure_function(queryset) -> None:
    print(queryset)
'''

IMPURE_FUNCTION_WITHOUT_PURE_IN_NAME = '''
def plain_function(queryset) -> None:
    print(queryset)
'''

FUNCTION_WITH_PURE_AS_SUBSTRING = '''
def purely_impure(queryset) -> None:
    print(queryset)
'''

ASYNC_PURE_FUNCTION = '''
async def pure_add(number: int) -> int:
    return number + 1
'''

ASYNC_IMPURE_FUNCTION_WITH_PURE_IN_NAME = '''
async def not_pure_function(queryset) -> None:
    print(queryset)
'''


@pytest.mark.parametrize(
    ('source', 'has_error'),
    [
        (PURE_FUNCTION, False),
        (IMPURE_FUNCTION_WITH_PURE_IN_NAME, True),
        (IMPURE_FUNCTION_WITHOUT_PURE_IN_NAME, False),
        (FUNCTION_WITH_PURE_AS_SUBSTRING, False),
        (ASYNC_PURE_FUNCTION, False),
        (ASYNC_IMPURE_FUNCTION_WITH_PURE_IN_NAME, True),
    ],
    ids=[
        'pure-function-is-ok',
        'impure-function-marked-as-pure',
        'impure-function-is-not-checked',
        'pure-only-as-substring-is-not-checked',
        'async-pure-function-is-ok',
        'async-impure-function-marked-as-pure',
    ],
)
def test__check_purity_of_functions__checks_only_functions_marked_as_pure(
    source,
    has_error,
    parse_funcdef,
):
    """
    Arrange: sync and async functions with, without, and merely containing 'pure'
    Act: check the purity of the function
    Assert: only an impure function with 'pure' as a name word is reported
    """
    func_def = parse_funcdef(source)

    error = check_purity_of_functions(func_def)

    assert (error is not None) is has_error


def test__check_purity_of_functions__error_message(parse_funcdef):
    """
    Arrange: an impure function with 'pure' in its name
    Act: get the reported error
    Assert: the message contains CFQ003 and the function name
    """
    func_def = parse_funcdef(IMPURE_FUNCTION_WITH_PURE_IN_NAME)

    error = check_purity_of_functions(func_def)

    assert error is not None
    assert error[2] == 'CFQ003 Function "not_pure_function" is not pure.'


def test__check_purity_of_functions__delegates_the_verdict_to_is_function_pure(
    parse_funcdef,
    mocker,
):
    """
    Arrange: a function named as pure and a mocked purity check
    Act: check the purity of the function
    Assert: the reported error follows the mocked verdict
    """
    mocked_is_function_pure = mocker.patch(
        'flake8_functions.function_purity.is_function_pure',
        return_value=False,
    )
    func_def = parse_funcdef(PURE_FUNCTION)

    error = check_purity_of_functions(func_def)

    mocked_is_function_pure.assert_called_once_with(func_def)
    assert error is not None


NO_VIOLATIONS = PURE_FUNCTION

CALLS_FORBIDDEN_FUNCTION = '''
def foo(queryset):
    print(queryset)
    return queryset
'''

ACCESSES_FORBIDDEN_ATTRIBUTE = '''
def foo(queryset):
    return queryset.count()
'''

USES_EXTERNAL_NAME = '''
def foo(number):
    return number + EXTERNAL_CONSTANT
'''

USES_ONLY_ARGS_LOCALS_AND_BUILTINS = '''
def foo(items):
    total = sum(items)
    return total
'''

HAS_NO_RETURN_OR_YIELD = '''
def foo(number):
    number + 1
'''

IS_A_GENERATOR = '''
def foo(items):
    for item in items:
        yield item
'''

MUTATES_ARGUMENT_VIA_AUGASSIGN = '''
def foo(total):
    total += 1
    return total
'''

MUTATES_ARGUMENT_VIA_SUBSCRIPT_ASSIGN = '''
def foo(items):
    items[0] = None
    return items
'''

MUTATES_ARGUMENT_VIA_ATTRIBUTE_ASSIGN = '''
def foo(entity):
    entity.name = 'renamed'
    return entity
'''

MUTATES_ARGUMENT_VIA_METHOD_CALL = '''
def foo(items):
    items.append(1)
    return items
'''

REASSIGNS_LOCAL_VARIABLE_NOT_ARGUMENT = '''
def foo(number):
    total = 0
    total += number
    return total
'''

UNPACKS_TUPLE_IN_FOR_LOOP = '''
def foo(pairs):
    total = 0
    for key, value in pairs:
        total += value
    return total
'''

DECLARES_ANNOTATED_LOCAL_VARIABLE = '''
def foo(number):
    total: int = number
    return total
'''

ASSIGNS_TO_UNRELATED_SUBSCRIPT_TARGET = '''
def foo(items):
    other = [None]
    other[0] = items
    return other
'''

ASSIGNS_ATTRIBUTE_OF_UNRELATED_OBJECT = '''
def foo(number):
    other = Box()
    other.value = number
    return other
'''

ANNOTATES_ATTRIBUTE_NOT_A_LOCAL_VARIABLE = '''
def foo(box, number):
    box.value: int = number
    return box
'''

UNPACKS_LIST_PATTERN_IN_FOR_LOOP = '''
def foo(pairs):
    total = 0
    for [key, value] in pairs:
        total += value
    return total
'''

HAS_LOCAL_IMPORT = '''
def foo(number):
    import math
    return math.floor(number)
'''

HAS_FORBIDDEN_ARGUMENT_TYPE = '''
def foo(queryset: QuerySet) -> int:
    return 1
'''

USES_SELF = '''
def foo(self, number):
    return self.value + number
'''

USES_CLS = '''
def foo(cls, number):
    return cls.value + number
'''

ASYNC_AWAITS_ONLY_ARGS = '''
async def foo(session, url):
    response = await session.get(url)
    return response
'''

ASYNC_WITH_MUTATES_ARGUMENT = '''
async def foo(entity):
    async with lock:
        entity.name = 'renamed'
    return entity
'''

ASYNC_NESTED_DEF_USES_OWN_ARGS_ONLY = '''
async def foo(items):
    async def helper(item):
        return item * 2
    return [await helper(item) for item in items]
'''

# `async for` targets are not recognized as local variables: the vendored
# purity check (like the mr-proper release it was ported from) only scans
# plain `for` loops and comprehensions for local-variable targets, so `item`
# below reads as an external name even though it is clearly loop-local.
ASYNC_FOR_TARGET_NOT_RECOGNIZED_AS_LOCAL = '''
async def foo(source):
    async for item in source:
        yield item
'''


@pytest.mark.parametrize(
    ('source', 'expected_purity'),
    [
        (NO_VIOLATIONS, True),
        (CALLS_FORBIDDEN_FUNCTION, False),
        (ACCESSES_FORBIDDEN_ATTRIBUTE, False),
        (USES_EXTERNAL_NAME, False),
        (USES_ONLY_ARGS_LOCALS_AND_BUILTINS, True),
        (HAS_NO_RETURN_OR_YIELD, False),
        (IS_A_GENERATOR, True),
        (MUTATES_ARGUMENT_VIA_AUGASSIGN, False),
        (MUTATES_ARGUMENT_VIA_SUBSCRIPT_ASSIGN, False),
        (MUTATES_ARGUMENT_VIA_ATTRIBUTE_ASSIGN, False),
        (MUTATES_ARGUMENT_VIA_METHOD_CALL, False),
        (REASSIGNS_LOCAL_VARIABLE_NOT_ARGUMENT, True),
        (UNPACKS_TUPLE_IN_FOR_LOOP, True),
        (DECLARES_ANNOTATED_LOCAL_VARIABLE, True),
        (ASSIGNS_TO_UNRELATED_SUBSCRIPT_TARGET, True),
        (ASSIGNS_ATTRIBUTE_OF_UNRELATED_OBJECT, True),
        (ANNOTATES_ATTRIBUTE_NOT_A_LOCAL_VARIABLE, True),
        (UNPACKS_LIST_PATTERN_IN_FOR_LOOP, False),
        (HAS_LOCAL_IMPORT, False),
        (HAS_FORBIDDEN_ARGUMENT_TYPE, False),
        (USES_SELF, False),
        (USES_CLS, False),
        (ASYNC_AWAITS_ONLY_ARGS, True),
        (ASYNC_WITH_MUTATES_ARGUMENT, False),
        (ASYNC_NESTED_DEF_USES_OWN_ARGS_ONLY, True),
        (ASYNC_FOR_TARGET_NOT_RECOGNIZED_AS_LOCAL, False),
    ],
    ids=[
        'no-violations-is-pure',
        'calls-forbidden-function',
        'accesses-forbidden-attribute',
        'uses-external-name',
        'uses-only-args-locals-and-builtins',
        'has-no-return-or-yield',
        'generator-with-yield-is-fine',
        'mutates-argument-via-augassign',
        'mutates-argument-via-subscript-assign',
        'mutates-argument-via-attribute-assign',
        'mutates-argument-via-mutating-method-call',
        'reassigns-local-variable-not-argument',
        'unpacks-tuple-in-for-loop',
        'declares-annotated-local-variable',
        'assigns-to-unrelated-subscript-target',
        'assigns-attribute-of-unrelated-object',
        'annotates-attribute-not-a-local-variable',
        'list-pattern-loop-target-is-not-recognized-as-local',
        'has-local-import',
        'has-forbidden-argument-type',
        'uses-self',
        'uses-cls',
        'async-await-of-only-args-is-fine',
        'async-with-mutates-argument',
        'async-nested-def-uses-own-args-only',
        'async-for-target-not-recognized-as-local',
    ],
)
def test__is_function_pure__success_case(source, expected_purity, parse_funcdef):
    """
    Arrange: functions each violating exactly one purity rule, and clean ones
    Act: check the function's purity
    Assert: every rule from the vendored purity checklist is enforced on its own
    """
    func_def = parse_funcdef(source)

    assert is_function_pure(func_def) is expected_purity
