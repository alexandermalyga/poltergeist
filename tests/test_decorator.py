import operator

import pytest

from poltergeist import Err, Ok, catch, catch_async


def test_decorator() -> None:
    decorated = catch(ZeroDivisionError)(operator.truediv)

    assert decorated(4, 2) == Ok(2)

    match decorated(4, 0):
        case Err(e):
            assert type(e) == ZeroDivisionError
            assert e.args == ("division by zero",)
        case _:
            pytest.fail("Should have been Err")


def test_decorator_other_error() -> None:
    # Only catching instances of ValueError
    decorated = catch(ValueError)(operator.truediv)

    assert decorated(4, 2) == Ok(2)

    # ZeroDivisionError should not have been catched
    with pytest.raises(ZeroDivisionError):
        decorated(4, 0)


def test_decorator_multiple_errors() -> None:
    decorated = catch(ZeroDivisionError, TypeError)(operator.truediv)

    assert decorated(4, 2) == Ok(2)

    match decorated(4, 0):
        case Err(e):
            assert type(e) == ZeroDivisionError
            assert e.args == ("division by zero",)
        case _:
            pytest.fail("Should have been Err")

    match decorated("4", 0):
        case Err(e):
            assert type(e) == TypeError
            assert e.args == ("unsupported operand type(s) for /: 'str' and 'int'",)
        case _:
            pytest.fail("Should have been Err")


async def test_async_decorator() -> None:
    async def async_div(a: float, b: float) -> float:
        return a / b

    decorated = catch_async(ZeroDivisionError)(async_div)

    assert await decorated(4, 2) == Ok(2)

    match await decorated(4, 0):
        case Err(e):
            assert type(e) == ZeroDivisionError
            assert e.args == ("division by zero",)
        case _:
            pytest.fail("Should have been Err")


async def test_async_decorator_other_error() -> None:
    async def async_div(a: float, b: float) -> float:
        return a / b

    # Only catching instances of ValueError
    decorated = catch_async(ValueError)(async_div)

    assert await decorated(4, 2) == Ok(2)

    # ZeroDivisionError should not have been catched
    with pytest.raises(ZeroDivisionError):
        await decorated(4, 0)


async def test_async_decorator_multiple_errors() -> None:
    async def async_div(a: float, b: float) -> float:
        return a / b

    decorated = catch_async(ZeroDivisionError, TypeError)(async_div)

    assert await decorated(4, 2) == Ok(2)

    match await decorated(4, 0):
        case Err(e):
            assert type(e) == ZeroDivisionError
            assert e.args == ("division by zero",)
        case _:
            pytest.fail("Should have been Err")

    match await decorated("4", 0):
        case Err(e):
            assert type(e) == TypeError
            assert e.args == ("unsupported operand type(s) for /: 'str' and 'int'",)
        case _:
            pytest.fail("Should have been Err")
