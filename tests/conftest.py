"""
Test Configuration and Fixtures
===============================

This module provides pytest configuration and fixtures for the test suite:
- Flask app factory for testing with in-memory database
- User authentication fixtures
- Database session management
- Common test data fixtures for lists and tasks
"""

import pytest
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from backend.models import db, User, TodoList, Task
from backend.auth import auth_bp
from backend.api import api_bp


def create_app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = False

    # Initialize extensions
    db.init_app(app)
    CORS(app, supports_credentials=True)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    """Authentication helper class."""

    class AuthActions:
        def __init__(self, client):
            self._client = client

        def register(
            self, username="testuser", email="test@example.com", password="testpass"
        ):
            return self._client.post(
                "/api/register",
                json={"username": username, "email": email, "password": password},
            )

        def login(self, username="test@example.com", password="testpass"):
            return self._client.post(
                "/api/login", json={"username": username, "password": password}
            )

        def logout(self):
            return self._client.post("/api/logout")

    return AuthActions(client)


@pytest.fixture
def user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Return a fresh instance to avoid DetachedInstanceError
    with app.app_context():
        return db.session.get(User, user_id)


@pytest.fixture
def todo_list(app, user):
    """Create a test todo list."""
    with app.app_context():
        # Get fresh user instance
        user_instance = db.session.get(User, user.id)
        todo_list = TodoList(
            name="Test List", description="A test todo list", user_id=user_instance.id
        )
        db.session.add(todo_list)
        db.session.commit()
        list_id = todo_list.id

    # Return fresh instance
    with app.app_context():
        return db.session.get(TodoList, list_id)


@pytest.fixture
def task(app, user, todo_list):
    """Create a test task."""
    with app.app_context():
        # Get fresh instances
        user_instance = db.session.get(User, user.id)
        list_instance = db.session.get(TodoList, todo_list.id)
        task = Task(
            title="Test Task",
            description="A test task",
            urgency="medium",
            list_id=list_instance.id,
            user_id=user_instance.id,
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    # Return fresh instance
    with app.app_context():
        return db.session.get(Task, task_id)
