"""Tests for auth endpoints."""

import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "username": "newuser", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client, auth_headers):
    resp = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "username": "another", "password": "password123"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    # register first
    await client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "username": "loginuser", "password": "password123"},
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    resp = await client.post(
        "/api/auth/login",
        json={"email": "nonexist@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_profile_requires_auth(client):
    resp = await client.get("/api/auth/profile")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_profile_with_auth(client, auth_headers):
    resp = await client.get("/api/auth/profile", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_quota(client, auth_headers):
    resp = await client.get("/api/auth/quota", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["quota_limit"] >= data["quota_used"]
    assert "remaining" in data
