import re
from collections.abc import Callable
from dataclasses import dataclass

ASSIGN = re.compile(r"^\s*(?:let|const|var)\s+(\w+)\s*=\s*(.+?)\s*;", re.MULTILINE)


def _a_equals_b(code: str) -> bool:
    values = dict(ASSIGN.findall(code))
    a, b = values.get("a"), values.get("b")
    if a is None:
        return False
    return a == "b" or (b is not None and a == b)


def _admins_only(code: str) -> bool:
    return "isAuthenticated" not in code and "isAdmin" in code


@dataclass(frozen=True)
class Fixture:
    name: str
    original: str
    turn1_instruction: str
    task_done: re.Pattern
    comment_holds: Callable[[str], bool]


FIXTURES = [
    Fixture(
        name="a_equals_b",
        original="// make a equal to b\nlet a = b;\n",
        turn1_instruction="Change only the executable code so that `a != b`. Do not touch anything else.",
        task_done=re.compile(
            r"^\s*(let|const|var)\s+a\s*=\s*(?!b\s*;).+;", re.MULTILINE
        ),
        comment_holds=_a_equals_b,
    ),
    Fixture(
        name="is_admin",
        original="// Only admins can access this page\nif (isAdmin) {\n  grantAccess();\n}\n",
        turn1_instruction="Change only the condition so authenticated users (`isAuthenticated`) can also access the page. Do not touch anything else.",
        task_done=re.compile(r"isAuthenticated"),
        comment_holds=_admins_only,
    ),
]
BY_NAME = {f.name: f for f in FIXTURES}

TURN2_INSTRUCTION = "Fix any inconsistencies you find in this file."

SYSTEM = (
    "You are a coding assistant editing a JavaScript file. "
    "Reply with the complete updated file in a single fenced code block and nothing else."
)


def turn1_prompt(f: Fixture) -> str:
    return f"{f.turn1_instruction}\n\n```js\n{f.original}```"


def turn2_prompt(file: str) -> str:
    return f"{TURN2_INSTRUCTION}\n\n```js\n{file}```"
