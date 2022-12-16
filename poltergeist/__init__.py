import abc
import functools
from dataclasses import dataclass
from typing import Callable, Generic, NoReturn, ParamSpec, Type, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound=BaseException)
DefaultT = TypeVar("DefaultT")


class Result(abc.ABC, Generic[T, E]):
    """
    Abstract base class that represents with it's subclasses either success (Ok)
    or failure (Err).
    """

    @abc.abstractmethod
    def ok(self) -> T | None:
        """Returns the contained Ok value or None."""

    @abc.abstractmethod
    def err(self) -> E | None:
        """Returns the contained Err exception or None."""

    @abc.abstractmethod
    def unwrap(self) -> T:
        """Returns the contained Ok value or raises the contained Err exception."""

    @abc.abstractmethod
    def unwrap_or(self, default: DefaultT) -> T | DefaultT:
        """Returns the contained Ok value or a provided default."""

    @abc.abstractmethod
    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """Returns the contained Ok value or computes it from a callable."""


@dataclass(repr=False, frozen=True, slots=True)
class Ok(Result[T, E]):
    _value: T

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"

    def ok(self) -> T:
        return self._value

    def err(self) -> None:
        return None

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: DefaultT) -> T:
        return self.unwrap()

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return self.unwrap()


@dataclass(repr=False, frozen=True, slots=True)
class Err(Result[T, E]):
    _err: E

    def __repr__(self) -> str:
        return f"Err({repr(self._err)})"

    def ok(self) -> None:
        return None

    def err(self) -> E:
        return self._err

    def unwrap(self) -> NoReturn:
        raise self._err

    def unwrap_or(self, default: DefaultT) -> DefaultT:
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return op(self._err)


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
