import pytest

from control_plane.core.auth import (
    hash_password,
    hash_session_token,
    new_session_token,
    normalize_email,
    verify_password,
)


def test_email_is_normalized() -> None:
    assert normalize_email("  USER@Example.COM ") == "user@example.com"


def test_passwords_use_verifiable_argon2_hashes() -> None:
    password_hash = hash_password("correct horse battery staple")
    assert password_hash.startswith("$argon2")
    assert verify_password(password_hash, "correct horse battery staple")
    assert not verify_password(password_hash, "incorrect password")


def test_session_tokens_are_random_and_only_hashed_for_storage() -> None:
    token = new_session_token()
    assert token != new_session_token()
    assert len(hash_session_token(token)) == 32


@pytest.mark.parametrize("password", ["short", "x" * 1025])
def test_invalid_password_lengths_are_rejected(password: str) -> None:
    with pytest.raises(ValueError):
        hash_password(password)
