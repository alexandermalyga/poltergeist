import functools
from dataclasses import dataclass
from typing import Callable, Generic, NoReturn, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound=BaseException)


@dataclass(repr=False, frozen=True, slots=True)
class Ok(Generic[T, E]):
    _value: T

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"

    def unwrap(self) -> T:
        return self._value


@dataclass(repr=False, frozen=True, slots=True)
class Err(Generic[T, E]):
    _err: E

    def __repr__(self) -> str:
        return f"Err({repr(self._err)})"

    def unwrap(self) -> NoReturn:
        raise self._err


Result = Ok[T, E] | Err[T, E]


def poltergeist(
    func: Callable[P, T]
) -> Callable[P, Ok[T, Exception] | Err[T, Exception]]:
    @functools.wraps(func)
    def wrapper(
        *args: P.args, **kwargs: P.kwargs
    ) -> Ok[T, Exception] | Err[T, Exception]:
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            return Err(e)
        return Ok(result)

    return wrapper
