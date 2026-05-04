"""Test security utilities — JWT and bcrypt."""

from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_hash_and_verify_password():
    password = "mysecretpassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_and_decode_access_token():
    token = create_access_token(
        user_id="test-uuid-123",
        role="job_seeker",
        tenant_id="tenant-uuid-456",
    )
    assert isinstance(token, str)
    assert len(token) > 50

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test-uuid-123"
    assert payload["role"] == "job_seeker"
    assert payload["tenant_id"] == "tenant-uuid-456"
    assert payload["type"] == "access"


def test_decode_invalid_token():
    result = decode_access_token("invalid.token.here")
    assert result is None


def test_create_refresh_token():
    token = create_refresh_token()
    assert isinstance(token, str)
    assert len(token) == 64  # 32 bytes hex = 64 chars


def test_hash_refresh_token():
    token = create_refresh_token()
    hashed = hash_refresh_token(token)
    assert hashed != token
    assert hash_refresh_token(token) == hashed  # deterministic
