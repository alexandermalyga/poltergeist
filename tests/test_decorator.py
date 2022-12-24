import operator

import pytest

from poltergeist import Err, Ok, poltergeist


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
