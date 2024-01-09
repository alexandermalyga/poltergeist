from typing import Any, Callable, Generic, NoReturn, TypeVar, final, overload

_T = TypeVar("_T")
_E = TypeVar("_E", bound=BaseException)
_D = TypeVar("_D")


@final
class Ok(Generic[_T]):
    __slots__ = ("_value",)
    __match_args__ = ("_value",)

    def __init__(self, value: _T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"

    def __eq__(self, __o: Any) -> bool:
        return isinstance(__o, Ok) and self._value == __o._value

    def err(self) -> None:
        return None

    def unwrap(self) -> _T:
        return self._value

    @overload
    def unwrap_or(self) -> _T:
        ...

    @overload
    def unwrap_or(self, default: Any) -> _T:
        ...

    def unwrap_or(self, default: Any = None) -> Any:
        return self.unwrap()

    def unwrap_or_else(self, op: Any) -> _T:
        return self.unwrap()


@final
class Err(Generic[_E]):
    __slots__ = ("_value",)
    __match_args__ = ("_value",)

    def __init__(self, value: _E) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"Err({repr(self._value)})"

    def __eq__(self, __o: Any) -> bool:
        return (
            isinstance(__o, Err)
            and type(__o._value) is type(self._value)
            and __o._value.args == self._value.args
        )

    def err(self) -> _E:
        return self._value

    def unwrap(self) -> NoReturn:
        raise self._value

    @overload
    def unwrap_or(self) -> None:
        ...

    @overload
    def unwrap_or(self, default: _D) -> _D:
        ...

    def unwrap_or(self, default: Any = None) -> Any:
        return default

    def unwrap_or_else(self, op: Callable[[_E], _D]) -> _D:
        return op(self._value)


Result = Ok[_T] | Err[_E]
