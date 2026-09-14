"""generate_project_code produces the six-character code, never person-supplied."""

from __future__ import annotations

import string

from app.domain.project_code import generate_project_code

_ALPHABET = set(string.ascii_uppercase + string.digits)


def test_code_is_six_characters_from_the_allowed_alphabet():
    code = generate_project_code()
    assert len(code) == 6
    assert set(code) <= _ALPHABET


def test_codes_are_not_all_identical():
    codes = {generate_project_code() for _ in range(20)}
    assert len(codes) > 1
