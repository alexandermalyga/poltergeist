import abc
import functools
from dataclasses import dataclass
from typing import Callable, Generic, NoReturn, ParamSpec, Type, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound=BaseException)


class Result(abc.ABC, Generic[T, E]):
    @abc.abstractmethod
    def unwrap(self) -> T:
        ...

    @abc.abstractmethod
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        ...


@dataclass(repr=False, frozen=True, slots=True)
class Ok(Result[T, E]):
    _value: T

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"

    def unwrap(self) -> T:
        return self._value

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return self.unwrap()


@dataclass(repr=False, frozen=True, slots=True)
class Err(Result[T, E]):
    _err: E

    def __repr__(self) -> str:
        return f"Err({repr(self._err)})"

    def unwrap(self) -> NoReturn:
        raise self._err

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return func(self._err)


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
