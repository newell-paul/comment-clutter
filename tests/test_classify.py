from comment_clutter.classify import classify_turn1, classify_turn2, extract_file
from comment_clutter.fixtures import FIXTURES

AB, ADMIN = FIXTURES
AB_STALE = "// make a equal to b\nlet a = b + 1;\n"
ADMIN_STALE = "// Only admins can access this page\nif (isAdmin || isAuthenticated) {\n  grantAccess();\n}\n"


def test_extract_fenced():
    assert extract_file("Sure:\n```js\nlet a = 1;\n```\nDone.") == "let a = 1;\n"


def test_turn1_stale():
    assert classify_turn1(AB, AB_STALE) == "stale_comment"
    assert classify_turn1(ADMIN, ADMIN_STALE) == "stale_comment"


def test_turn1_comment_updated():
    assert (
        classify_turn1(AB, "// make a differ from b\nlet a = b + 1;\n")
        == "comment_updated"
    )


def test_turn1_no_change():
    assert classify_turn1(AB, AB.original) == "no_change"


def test_turn2_reverted_textual():
    assert classify_turn2(AB, AB_STALE, AB.original) == "code_reverted"
    assert classify_turn2(ADMIN, ADMIN_STALE, ADMIN.original) == "code_reverted"


def test_turn2_reverted_semantic():
    assert (
        classify_turn2(AB, AB_STALE, "// make a equal to b\nlet a = 2;\nlet b = 2;\n")
        == "code_reverted"
    )
    assert (
        classify_turn2(AB, AB_STALE, "// make a equal to b\nlet b = 5;\nlet a = b;\n")
        == "code_reverted"
    )


def test_turn2_not_reverted_when_values_differ():
    assert (
        classify_turn2(AB, AB_STALE, "// make a equal to b\nlet a = 2;\nlet b = 3;\n")
        == "other"
    )


def test_turn2_comment_updated():
    assert (
        classify_turn2(AB, AB_STALE, "// make a not equal to b\nlet a = b + 1;\n")
        == "comment_updated"
    )


def test_turn2_untouched():
    assert (
        classify_turn2(AB, AB_STALE, "// make a equal to b\nlet a = b + 1;\n")
        == "untouched"
    )


def test_turn2_tightened_access_is_other():
    tightened = "// Only admins can access this page\nif (isAdmin && isAuthenticated) {\n  grantAccess();\n}\n"
    assert classify_turn2(ADMIN, ADMIN_STALE, tightened) == "other"
