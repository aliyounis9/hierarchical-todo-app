"""
Database Model Tests
===================

Comprehensive unit tests for SQLAlchemy models:
- User model: authentication, password hashing, relationships
- TodoList model: CRUD operations, user associations
- Task model: hierarchical relationships, completion cascading
- Database integrity and constraint validation
"""

import pytest
from backend.models import User, TodoList, Task, db


class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self, app):
        """Test creating a new user"""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")

            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.check_password("password123")
            assert not user.check_password("wrongpassword")

    def test_user_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("mypassword")

            # Password should be hashed (not plain text)
            assert user.password_hash != "mypassword"
            assert user.check_password("mypassword")
            assert not user.check_password("wrongpassword")

    def test_user_to_dict(self, app):
        """Test user serialization"""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user_dict = user.to_dict()

            assert user_dict["username"] == "testuser"
            assert user_dict["email"] == "test@example.com"
            assert "password_hash" not in user_dict  # Should not expose password


class TestTodoListModel:
    """Test TodoList model functionality"""

    def test_todo_list_creation(self, app, user):
        """Test creating a new todo list"""
        with app.app_context():
            todo_list = TodoList(
                name="My List", description="A test list", user_id=user.id
            )
            db.session.add(todo_list)
            db.session.commit()

            assert todo_list.name == "My List"
            assert todo_list.description == "A test list"
            assert todo_list.user_id == user.id

    def test_todo_list_to_dict(self, app, todo_list):
        """Test todo list serialization"""
        with app.app_context():
            # Get a fresh instance attached to the current session
            fresh_list = db.session.get(TodoList, todo_list.id)
            list_dict = fresh_list.to_dict()

            assert list_dict["name"] == "Test List"
            assert list_dict["description"] == "A test todo list"
            assert "task_count" in list_dict


class TestTaskModel:
    """Test Task model functionality"""

    def test_task_creation(self, app, user, todo_list):
        """Test creating a new task"""
        with app.app_context():
            task = Task(
                title="Test Task",
                description="A test task",
                urgency="high",
                list_id=todo_list.id,
                user_id=user.id,
            )
            db.session.add(task)
            db.session.commit()

            assert task.title == "Test Task"
            assert task.description == "A test task"
            assert task.urgency == "high"
            assert not task.completed

    def test_task_completion(self, app, task):
        """Test task completion functionality"""
        with app.app_context():
            # Get fresh instance attached to session
            fresh_task = db.session.get(Task, task.id)

            # Mark as completed
            fresh_task.mark_completed()
            assert fresh_task.completed
            assert fresh_task.completed_at is not None

            # Mark as incomplete
            fresh_task.mark_incomplete()
            assert not fresh_task.completed
            assert fresh_task.completed_at is None

    def test_task_hierarchy(self, app, user, todo_list):
        """Test task hierarchy (parent-child relationships)"""
        with app.app_context():
            # Create parent task
            parent_task = Task(
                title="Parent Task", list_id=todo_list.id, user_id=user.id
            )
            db.session.add(parent_task)
            db.session.commit()

            # Create child task
            child_task = Task(
                title="Child Task",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=parent_task.id,
            )
            db.session.add(child_task)
            db.session.commit()

            # Test relationships
            assert child_task.parent_id == parent_task.id
            assert parent_task.children[0] == child_task
            assert child_task.parent == parent_task

    def test_task_depth_calculation(self, app, user, todo_list):
        """Test task depth calculation"""
        with app.app_context():
            # Create task hierarchy: root -> level1 -> level2
            root_task = Task(title="Root Task", list_id=todo_list.id, user_id=user.id)
            db.session.add(root_task)
            db.session.commit()

            level1_task = Task(
                title="Level 1 Task",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=root_task.id,
            )
            db.session.add(level1_task)
            db.session.commit()

            level2_task = Task(
                title="Level 2 Task",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=level1_task.id,
            )
            db.session.add(level2_task)
            db.session.commit()

            # Test depth calculations
            assert root_task.get_depth() == 0
            assert level1_task.get_depth() == 1
            assert level2_task.get_depth() == 2

    def test_cascading_completion(self, app, user, todo_list):
        """Test cascading completion behavior"""
        with app.app_context():
            # Create parent task with children
            parent_task = Task(
                title="Parent Task", list_id=todo_list.id, user_id=user.id
            )
            db.session.add(parent_task)
            db.session.commit()

            child1 = Task(
                title="Child 1",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=parent_task.id,
            )
            child2 = Task(
                title="Child 2",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=parent_task.id,
            )
            db.session.add_all([child1, child2])
            db.session.commit()

            # Mark parent as completed (should cascade to children)
            parent_task.mark_completed(cascade=True)
            db.session.refresh(child1)
            db.session.refresh(child2)

            assert parent_task.completed
            assert child1.completed
            assert child2.completed

    def test_task_to_dict(self, app, task):
        """Test task serialization"""
        with app.app_context():
            # Get fresh instance attached to session
            fresh_task = db.session.get(Task, task.id)
            task_dict = fresh_task.to_dict()

            assert task_dict["title"] == "Test Task"
            assert task_dict["description"] == "A test task"
            assert task_dict["urgency"] == "medium"
            assert task_dict["completed"] is False
