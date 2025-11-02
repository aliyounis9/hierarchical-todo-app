"""
Authentication System Tests
==========================

Tests for user authentication endpoints and functionality:
- User registration with validation
- Login/logout session management
- Password security and hashing
- Authentication state checking
- Error handling for invalid credentials
"""

import pytest
import json
from backend.models import User, db


class TestAuth:
    """Test authentication endpoints"""

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Registration successful"
        assert "user" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "new@example.com"

    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post(
            "/api/register",
            json={
                "username": "newuser"
                # Missing email and password
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_register_duplicate_email(self, client, user):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/register",
            json={
                "username": "anotheruser",
                "email": "test@example.com",  # Already exists
                "password": "password123",
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already registered" in data["error"]

    def test_login_success(self, client, user):
        """Test successful login"""
        response = client.post(
            "/api/login", json={"username": "test@example.com", "password": "testpass"}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Login successful"
        assert "user" in data

    def test_login_invalid_credentials(self, client, user):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/login",
            json={"username": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post(
            "/api/login",
            json={"username": "nonexistent@example.com", "password": "password"},
        )

        assert response.status_code == 401

    def test_logout(self, client, auth):
        """Test logout functionality"""
        auth.login()

        response = client.post("/api/logout")
        assert response.status_code == 200

    def test_protected_route_without_auth(self, client):
        """Test accessing protected route without authentication"""
        response = client.get("/api/lists")
        assert response.status_code == 302  # Redirect to login

    def test_protected_route_with_auth(self, client, auth):
        """Test accessing protected route with authentication"""
        # Register and login
        auth.register()
        auth.login()

        # Access protected route
        response = client.get("/api/lists")
        assert response.status_code == 200
