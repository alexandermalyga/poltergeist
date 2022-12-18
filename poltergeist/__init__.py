import functools
from dataclasses import dataclass
from typing import Any, Callable, Generic, NoReturn, ParamSpec, Type, TypeVar, overload

P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound=BaseException)
DefaultT = TypeVar("DefaultT")


@dataclass(repr=False, frozen=True, slots=True)
class Ok(Generic[T, E]):
    _value: T

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"

    def err(self) -> None:
        return None

    def unwrap(self) -> T:
        return self._value

    @overload
    def unwrap_or(self) -> T:
        ...

    @overload
    def unwrap_or(self, default: DefaultT) -> T:
        ...

    def unwrap_or(self, default: Any = None) -> Any:
        return self.unwrap()

    def unwrap_or_else(self, op: Callable[[E], DefaultT]) -> T:
        return self.unwrap()


@dataclass(repr=False, frozen=True, slots=True)
class Err(Generic[T, E]):
    _err: E

    def __repr__(self) -> str:
        return f"Err({repr(self._err)})"

    def err(self) -> E:
        return self._err

    def unwrap(self) -> NoReturn:
        raise self._err

    @overload
    def unwrap_or(self) -> None:
        ...

    @overload
    def unwrap_or(self, default: DefaultT) -> DefaultT:
        ...

    def unwrap_or(self, default: Any = None) -> Any:
        return default

    def unwrap_or_else(self, op: Callable[[E], DefaultT]) -> DefaultT:
        return op(self._err)


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
