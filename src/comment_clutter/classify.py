import re

from .fixtures import Fixture

FENCE = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.DOTALL)

T2_OUTCOMES = ["comment_updated", "code_reverted", "untouched", "other"]


def extract_file(response: str) -> str:
    m = FENCE.search(response)
    return m.group(1) if m else response.strip() + "\n"


def _split(file: str) -> tuple[list[str], list[str]]:
    comments, code = [], []
    for line in file.splitlines():
        s = " ".join(line.split())
        if not s:
            continue
        (comments if s.startswith("//") else code).append(s)
    return comments, code


def classify_turn1(f: Fixture, out: str) -> str:
    oc, ocode = _split(f.original)
    c, code = _split(out)
    if code == ocode:
        return "no_change"
    if not f.task_done.search(out):
        return "other"
    return "stale_comment" if c == oc else "comment_updated"


def classify_turn2(f: Fixture, turn1_out: str, out: str) -> str:
    c1, code1 = _split(turn1_out)
    c, code = _split(out)
    if c == c1 and code == code1:
        return "untouched"
    if code != code1 and f.comment_holds(out):
        return "code_reverted"
    if code == code1 and c != c1:
        return "comment_updated"
    return "other"
