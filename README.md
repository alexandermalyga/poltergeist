# poltergeist

Experimental Rust-like error handling in Python, with type-safety in mind.

## Examples

Use the provided `@poltergeist` decorator on any function:

```python
from pathlib import Path
from poltergeist import Err, Ok, poltergeist

@poltergeist(FileNotFoundError)
def read_text(path: Path) -> str:
    return path.read_text()

result = read_text(Path("test.txt"))

# Handle errors using structural pattern matching
match result:
    case Ok(content):
        # Type-checkers know that content is a string,
        # carried over from the return type of the original function.
        print("File content:", content)
    case Err(e):
        # The exception type is also known
        print("File not found:", e.filename)

# Or directly get the returned value
# This will raise the original exception, if there was one
content = result.unwrap()
```

You can also wrap errors yourself:

```python
from pathlib import Path
from poltergeist import Err, Ok, Result

def read_text(path: Path) -> Result[str, FileNotFoundError]:
    try:
        return Ok(path.read_text())
    except FileNotFoundError as e:
        return Err(e)
```

Both of these examples pass type checking and provide in-editor autocompletion.
