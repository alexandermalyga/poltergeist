import operator
from typing import Any

import pytest

from poltergeist import Err, Ok, poltergeist


def test_ok() -> None:
    result: Ok[str, Exception] = Ok("abc")

    match result:
        case Ok(v):
            assert v == "abc"
        case _:
            pytest.fail("Should have been Ok")

    assert result.unwrap() == "abc"
    assert result.unwrap_or_else(lambda e: str(e)) == "abc"


def test_error() -> None:
    result: Err[Any, ValueError] = Err(ValueError("abc"))

    match result:
        case Err(e):
            assert type(e) == ValueError
            assert e.args == ("abc",)
        case _:
            pytest.fail("Should have been Err")

    with pytest.raises(ValueError) as excinfo:
        result.unwrap()

    assert type(excinfo.value) == ValueError
    assert excinfo.value.args == ("abc",)

    assert result.unwrap_or_else(lambda e: f"Exception is {e}") == "Exception is abc"


def test_decorator() -> None:
    decorated = poltergeist(ZeroDivisionError)(operator.truediv)

    assert decorated(4, 2) == Ok(2)

    match decorated(4, 0):
        case Err(e):
            assert type(e) == ZeroDivisionError
            assert e.args == ("division by zero",)
        case _:
            pytest.fail("Should have been Err")


def test_decorator_other_error() -> None:
    # Only catching instances of ValueError
    decorated = poltergeist(ValueError)(operator.truediv)

    assert decorated(4, 2) == Ok(2)

    # ZeroDivisionError should not have been catched
    with pytest.raises(ZeroDivisionError):
        decorated(4, 0)
