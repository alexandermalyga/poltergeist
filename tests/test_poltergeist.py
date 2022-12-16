import operator
from typing import Any

import pytest

from poltergeist import Err, Ok, Result, poltergeist


def test_ok() -> None:
    result: Result[str, Exception] = Ok("abc")

    match result:
        case Ok(v):
            assert v == "abc"
        case _:
            pytest.fail("Should have been Ok")

    assert result.err() is None

    assert result.unwrap() == "abc"

    assert result.unwrap_or() == "abc"

    assert result.unwrap_or("aaa") == "abc"

    assert result.unwrap_or_else(lambda e: str(e)) == "abc"


def test_error() -> None:
    result: Result[str, ValueError] = Err(ValueError("abc"))

    match result:
        case Err(e):
            assert type(e) == ValueError
            assert e.args == ("abc",)
        case _:
            pytest.fail("Should have been Err")

    assert type(result.err()) == ValueError
    assert result.err().args == ("abc",)

    with pytest.raises(ValueError) as excinfo:
        result.unwrap()

    assert type(excinfo.value) == ValueError
    assert excinfo.value.args == ("abc",)

    assert result.unwrap_or() is None

    assert result.unwrap_or("aaa") == "aaa"

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
