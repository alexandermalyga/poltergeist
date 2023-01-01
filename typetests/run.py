import os
import re
import sys
from subprocess import PIPE, Popen
from typing import Optional

from comment_parser import comment_parser

ALERT = "\033[91m"
GOOD = "\033[92m"
RESET = "\033[0m"


class ParsingFailed(ValueError):
    pass


def run_mypy_tests(directory: str = "mypy"):
    current_path = sys.path[0]
    test_directory = os.path.join(current_path, directory)
    filepaths: list[str] = []
    errors = []
    print("\n")
    for dirpath, _, names in os.walk(test_directory):
        filepaths += [
            os.path.join(dirpath, name)
            for name in names
            if name.endswith(".py")
        ]
    for path in filepaths:
        errors += MyPyTestFile(current_path, path).check()
    print("\n")
    for expected, actual in errors:
        print(f"=== LINE {expected.linenumber} ===")
        message: str = ""
        if isinstance(expected, TypeOutcome):
            print(f"{'Expected type'.ljust(20)}{ALERT}{expected.revealed_type}{RESET}")
            if actual is None:
                print("No type note found. Did you forget to call `reveal_type`?")
            else:
                print(f"{'Found type'.ljust(20)}{GOOD}{actual.revealed_type}{RESET}")
        if isinstance(expected, ErrorOutcome):
            if expected.error is None:
                print("Expected error.")
            else:
                print(f"{'Expected error'.ljust(20)}{ALERT}{expected.error}{RESET}")
            if actual is None:
                print(f"No error found.")
            else:
                print(f"{'Found error'.ljust(20)}{GOOD}{actual.error}{RESET}")

        print(message)

    if errors:
        sys.exit(1)


class MyPyTestFile:
    def __init__(self, base_path: str, file_path: str) -> None:
        self.path = file_path
        self.rel_path = os.path.relpath(file_path, base_path)

    def _expected_outcomes(self) -> list["Outcome"]:
        expectations: list["Outcome"] = []
        for comment in comment_parser.extract_comments(self.path):
            text = comment.text()
            linenumber = comment.line_number()
            expectation = TypeOutcome.from_comment(
                linenumber, text
            ) or ErrorOutcome.from_comment(linenumber, text)
            if expectation is not None:
                expectations.append(expectation)
        return expectations

    def _mypy_outcomes(self) -> list["Outcome"]:
        actuals: list["Outcome"] = []
        command = ["mypy", self.path]
        process = Popen(command, stdout=PIPE)
        output, _ = process.communicate()
        for line in output.decode("utf-8").split("\n"):
            message = TypeOutcome.from_mypy_output(
                line
            ) or ErrorOutcome.from_mypy_output(line)
            if message is not None:
                actuals.append(message)
        return actuals

    def check(self) -> list[tuple["Outcome", Optional["Outcome"]]]:
        print(self.rel_path, end=" ")

        expected_outcomes = self._expected_outcomes()
        if not expected_outcomes:
            print("Found no expectations")
            return []

        actual_outcomes = self._mypy_outcomes()
        errors = []
        for expected in expected_outcomes:
            has_match = False
            for actual in actual_outcomes:
                if expected.linenumber != actual.linenumber:
                    continue
                has_match = True
                if expected == actual:
                    print(GOOD + "." + RESET, end="")
                    break

                print(ALERT + "F" + RESET, end="")
                errors.append((expected, actual))

            else:
                if not has_match:
                    errors.append((expected, None))

        return errors


class Outcome:
    @classmethod
    def from_mypy_output(cls, raw: str) -> Optional["Outcome"]:
        try:
            linenumber = Outcome._linenumber_from_mypy_output(raw)
            return Outcome(linenumber)
        except ParsingFailed:
            return None

    def __init__(self, linenumber) -> None:
        self.linenumber = linenumber

    @staticmethod
    def _linenumber_from_mypy_output(raw: str) -> int:
        match = re.search(".*\.py:(\d+):.*", raw)
        if match is None:
            raise ParsingFailed()
        return int(match.group(1))


class TypeOutcome(Outcome):

    comment_prefix: str = " expect-type: "

    @classmethod
    def from_mypy_output(cls, raw: str) -> Optional["TypeOutcome"]:
        super_instance = super(TypeOutcome, cls).from_mypy_output(raw)
        if super_instance is None:
            return None

        try:
            revealed_type = TypeOutcome._revealed_type_from_mypy_output(raw)
            return TypeOutcome(
                super_instance.linenumber,
                revealed_type,
            )
        except ParsingFailed:
            return None

    @classmethod
    def from_comment(
        cls,
        linenumber: int,
        comment: str,
    ) -> Optional["TypeOutcome"]:
        try:
            revealed_type = cls._revealed_type_from_comment(comment)
            return cls(linenumber, revealed_type)
        except ParsingFailed:
            return None

    def __init__(self, linenumber: str, revealed_type: str) -> None:
        super().__init__(linenumber)
        self.revealed_type = revealed_type

    def __repr__(self) -> str:
        return f"TypeOutcome({self.linenumber}, {self.revealed_type})"

    def __eq__(self, other: "TypeOutcome") -> bool:
        if not isinstance(other, TypeOutcome):
            return False
        return (
            self.revealed_type == other.revealed_type
            and self.linenumber == other.linenumber
        )

    @staticmethod
    def _revealed_type_from_mypy_output(raw: str) -> str:
        match = re.search('.*\.py:\d+: note: Revealed type is "(.*)"', raw)
        if match is None:
            raise ParsingFailed()
        return match.group(1)

    @classmethod
    def _revealed_type_from_comment(cls, comment: str) -> str:
        match = re.search(f"{cls.comment_prefix}(.*)", comment)
        if not match:
            raise ParsingFailed()
        return match.group(1)


class ErrorOutcome(Outcome):

    comment_prefix: str = "expect-error:"

    @classmethod
    def from_mypy_output(cls, raw: str) -> Optional["ErrorOutcome"]:
        super_instance = super(ErrorOutcome, cls).from_mypy_output(raw)
        if super_instance is None:
            return None

        try:
            error = cls._error_from_mypy_output(raw)
        except ParsingFailed:
            return None
        return cls(super_instance.linenumber, error)

    @staticmethod
    def _error_from_mypy_output(raw: str) -> str:
        match = re.search(".*\.py:\d+: error: (.*)", raw)
        try:
            return match.group(1)
        except AttributeError:
            raise ParsingFailed()

    @classmethod
    def from_comment(
        cls, linenumber: int, comment: str
    ) -> Optional["ErrorOutcome"]:
        comment = comment.strip()
        if comment.startswith(cls.comment_prefix):
            return cls(linenumber, comment[len(cls.comment_prefix) :].strip() or None)
        return None

    def __init__(self, linenumber: int, error: str | None) -> None:
        super().__init__(linenumber)
        self.error = error

    def __eq__(self, other: "ErrorOutcome") -> bool:
        if not isinstance(other, ErrorOutcome):
            return False

        if self.linenumber != other.linenumber:
            return False

        if self.error is None or other.error is None:
            # Error outcomes without specification are just checked for existence
            return True

        return self.error == other.error


if __name__ == "__main__":
    run_mypy_tests()
