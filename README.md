# poltergeist

[![pypi](https://img.shields.io/pypi/v/poltergeist.svg)](https://pypi.python.org/pypi/poltergeist)
[![versions](https://img.shields.io/pypi/pyversions/poltergeist.svg)](https://github.com/alexandermalyga/poltergeist)

Experimental Rust-like error handling in Python, with type-safety in mind.

## Installation

```
pip install poltergeist
```

## Examples

Use the provided `@poltergeist` decorator on any function:

```python
from pathlib import Path
from poltergeist import Err, Ok, Result, poltergeist

# Wrap a function to handle a concrete exception type (Exception by default)
@poltergeist(error=OSError)
def read_text(path: Path) -> str:
    return path.read_text()

# Now the function returns an object of type Result[str, OSError]
result = read_text(Path("test.txt"))
```

Or wrap errors manually:

```python
def read_text(path: Path) -> Result[str, FileNotFoundError]:
    try:
        return Ok(path.read_text())
    except FileNotFoundError as e:
        return Err(e)
```

Then handle the result:

```python
# Get the contained Ok value or raise the contained Err exception
content = result.unwrap()

# Get the contained Ok value or a default value
content = result.unwrap_or("default text")
content = result.unwrap_or()  # default None

# Get the contained Ok value or compute it from a callable
content = result.unwrap_or_else(lambda e: f"The exception was: {e}")

# Get the contained Err exception or None
err = result.err()

# Handle errors using structural pattern matching
match result:
    case Ok(content):
        print("File content in upper case:", content.upper())
    case Err(e):
        match e:
            case FileNotFoundError():
                print("File not found:", e.filename)
            case PermissionError():
                print("Permission error:", e.errno)
            case _:
                raise e
```
