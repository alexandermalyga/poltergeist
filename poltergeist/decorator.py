import functools
from typing import Callable, ParamSpec, Type, TypeVar

from poltergeist.result import Err, Ok, Result

P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound=BaseException)
DefaultT = TypeVar("DefaultT")


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
