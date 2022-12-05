import functools
from dataclasses import dataclass
from typing import Callable, Generic, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound=BaseException)


@dataclass(repr=False, frozen=True, slots=True)
class Ok(Generic[T, E]):
    _value: T

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"


@dataclass(repr=False, frozen=True, slots=True)
class Err(Generic[T, E]):
    _err: E

    def __repr__(self) -> str:
        return f"Err({repr(self._err)})"


Result = Ok[T, E] | Err[T, E]


def poltergeist(
    func: Callable[P, T] | None = None, /, *, error: E = Exception
) -> Callable[P, Result]:
    if func is None:
        # Means this was called as @poltergeist() with parenthesis
        return functools.partial(poltergeist, error=error)  # type: ignore

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result:
        try:
            return Ok(func(*args, **kwargs))
        except error as e:
            return Err(e)

    return wrapper
