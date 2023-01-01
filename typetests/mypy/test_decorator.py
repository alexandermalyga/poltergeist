from poltergeist import Err, Ok, Result, poltergeist


@poltergeist(error=ValueError)
def decorated_function(x: int) -> int:
    return x


reveal_type(decorated_function(1))  # expect-type: Union[poltergeist.result.Ok[builtins.int], poltergeist.result.Err[builtins.ValueError]]

poltergeist(error="not an exception")  # expect-error:
