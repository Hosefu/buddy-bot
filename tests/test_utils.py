import re
import string
import secrets

import pytest

from apps.common.utils import generate_random_string, generate_secure_token


def test_generate_random_string_default_length():
    result = generate_random_string()
    assert len(result) == 10
    allowed = string.ascii_letters + string.digits
    assert all(ch in allowed for ch in result)


def test_generate_random_string_letters_only():
    result = generate_random_string(length=15, include_digits=False, include_special=False)
    assert len(result) == 15
    allowed = string.ascii_letters
    assert all(ch in allowed for ch in result)


def test_generate_secure_token_length_and_hex():
    token = generate_secure_token(16)
    assert len(token) == 32
    assert re.fullmatch(r"[0-9a-f]+", token)


def test_generate_secure_token_uniqueness():
    token1 = generate_secure_token()
    token2 = generate_secure_token()
    assert token1 != token2
