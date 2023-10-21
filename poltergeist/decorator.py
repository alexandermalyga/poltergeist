import functools
from collections.abc import Awaitable
from typing import Callable, ParamSpec, Type

from poltergeist.result import E, Err, Ok, Result, T

P = ParamSpec("P")


def catch(
    *errors: Type[E],
) -> Callable[[Callable[P, T]], Callable[P, Result[T, E]]]:
    def decorator(func: Callable[P, T]) -> Callable[P, Result[T, E]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                result = func(*args, **kwargs)
            except errors as e:
                return Err(e)
            return Ok(result)

        return wrapper

    return decorator


def catch_async(
    *errors: Type[E],
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[Result[T, E]]]]:
    def decorator(
        func: Callable[P, Awaitable[T]]
    ) -> Callable[P, Awaitable[Result[T, E]]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                result = await func(*args, **kwargs)
            except errors as e:
                return Err(e)
            return Ok(result)

        return wrapper

    return decorator
