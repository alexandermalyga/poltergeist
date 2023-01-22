from typing import Any, Callable, Generic, NoReturn, TypeVar, final, overload

T = TypeVar("T")
E = TypeVar("E", bound=BaseException)
DefaultT = TypeVar("DefaultT")


@final
class Ok(Generic[T]):

    __slots__ = ("_value",)
    __match_args__ = ("_value",)

    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"

    def __eq__(self, __o: Any) -> bool:
        return isinstance(__o, Ok) and self._value == __o._value

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

    def unwrap_or_else(self, op: Any) -> T:
        return self.unwrap()


@final
class Err(Generic[E]):

    __slots__ = ("_error",)
    __match_args__ = ("_error",)

    def __init__(self, error: E) -> None:
        self._error = error

    def __repr__(self) -> str:
        return f"Err({repr(self._error)})"

    def __eq__(self, __o: Any) -> bool:
        return (
            isinstance(__o, Err)
            and type(__o._error) is type(self._error)
            and __o._error.args == self._error.args
        )

    def err(self) -> E:
        return self._error

    def unwrap(self) -> NoReturn:
        raise self._error

    @overload
    def unwrap_or(self) -> None:
        ...

    @overload
    def unwrap_or(self, default: DefaultT) -> DefaultT:
        ...

    def unwrap_or(self, default: Any = None) -> Any:
        return default

    def unwrap_or_else(self, op: Callable[[E], DefaultT]) -> DefaultT:
        return op(self._error)


Result = Ok[T] | Err[E]
