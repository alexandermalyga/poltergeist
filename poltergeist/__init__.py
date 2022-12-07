import functools
from dataclasses import dataclass
from typing import Callable, Generic, NoReturn, ParamSpec, Type, TypeVar

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
    error: Type[E],
) -> Callable[[Callable[P, T]], Callable[P, Result[T, E]]]:
    """
    Decorator that wraps the result of a function into an Ok object if it
    executes without raising an exception. Otherwise, returns an Err object with
    the exception raised by the function.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, Result[T, E]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                result = func(*args, **kwargs)
            except error as e:
                return Err(e)
            return Ok(result)

        return wrapper

    return decorator
