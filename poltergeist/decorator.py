import functools
from typing import Any, Callable, ParamSpec, Type, TypeVar, overload

from poltergeist.result import Err, Ok, Result

P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound=BaseException)


@overload
def poltergeist(func: Callable[P, T], /) -> Callable[P, Result[T, Exception]]:
    # Called as @poltergeist
    ...


@overload
def poltergeist() -> Callable[[Callable[P, T]], Callable[P, Result[T, Exception]]]:
    # Called as @poltergeist()
    ...


@overload
def poltergeist(
    *,
    error: Type[E],
) -> Callable[[Callable[P, T]], Callable[P, Result[T, E]]]:
    # Called as @poltergeist(error=SomeError)
    ...


def poltergeist(func: Any = None, /, *, error: Any = Exception) -> Any:
    """
    Decorator that wraps the result of a function into an Ok object if it
    executes without raising an exception. Otherwise, returns an Err object with
    the exception raised by the function.
    """

    if func is None:
        return functools.partial(poltergeist, error=error)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
        except error as e:
            return Err(e)
        return Ok(result)

    return wrapper
