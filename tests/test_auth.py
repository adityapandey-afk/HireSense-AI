"""Tests for authentication routes."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def test_register_and_login(client):
    # Register
    resp = client.post("/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123",
        "role": "candidate",
    })
    assert resp.status_code == 201
    assert "user_id" in resp.json()

    # Login
    resp = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "securepassword123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "candidate"


def test_register_duplicate_email(client):
    payload = {
        "full_name": "User A",
        "email": "dup@example.com",
        "password": "password123",
        "role": "recruiter",
    }
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "full_name": "Secure User",
        "email": "secure@example.com",
        "password": "rightpassword",
        "role": "candidate",
    })
    resp = client.post("/auth/login", json={
        "email": "secure@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_invalid_role(client):
    resp = client.post("/auth/register", json={
        "full_name": "Bad Role",
        "email": "badrole@example.com",
        "password": "password123",
        "role": "admin",
    })
    assert resp.status_code == 422


def test_weak_password(client):
    resp = client.post("/auth/register", json={
        "full_name": "Weak Pass",
        "email": "weak@example.com",
        "password": "123",
        "role": "candidate",
    })
    assert resp.status_code == 422
