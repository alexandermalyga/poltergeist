from dataclasses import dataclass
from typing import Any, Callable, Generic, NoReturn, TypeVar, overload

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
