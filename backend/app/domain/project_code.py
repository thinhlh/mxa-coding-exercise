"""Generates the project code the platform assigns; no part of it comes from a person."""

from __future__ import annotations

import secrets
import string

_ALPHABET = string.ascii_uppercase + string.digits
_CODE_LENGTH = 6


def generate_project_code() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(_CODE_LENGTH))
