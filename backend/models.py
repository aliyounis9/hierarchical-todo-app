"""
Database Models for Hierarchical Todo App
=========================================

This module defines the SQLAlchemy models for our application:
- User: User accounts with authentication
- TodoList: Collections of tasks belonging to users
- Task: Individual tasks with hierarchical relationships
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and task ownership"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    todo_lists = db.relationship(
        "TodoList", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    tasks = db.relationship(
        "Task", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and store the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary for JSON responses"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TodoList(db.Model):
    """Todo list model - containers for tasks"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tasks = db.relationship(
        "Task", backref="todo_list", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, include_tasks=False):
        """Convert list to dictionary, optionally include tasks"""
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "task_count": len(self.tasks),
        }

        if include_tasks:
            # Only include top-level tasks (no parent)
            top_level_tasks = [task for task in self.tasks if task.parent_id is None]
            result["tasks"] = [
                task.to_dict(include_children=True) for task in top_level_tasks
            ]

        return result


class Task(db.Model):
    """Task model with hierarchical relationships"""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    # low, medium, high, urgent
    urgency = db.Column(db.String(20), default="medium", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey("todo_list.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("task.id"))

    # Self-referential relationship for hierarchy
    children = db.relationship(
        "Task",
        backref=db.backref("parent", remote_side=[id]),
        lazy=True,
        cascade="all, delete-orphan",
    )

    def get_depth(self):
        """Calculate the depth of this task in the hierarchy"""
        if self.parent is None:
            return 0
        return self.parent.get_depth() + 1

    def mark_completed(self, cascade=True):
        """Mark task as completed with timestamp and cascade to children"""
        self.completed = True
        self.completed_at = datetime.utcnow()

        # Cascade down: mark all children as completed
        if cascade:
            for child in self.children:
                if not child.completed:
                    child.mark_completed(cascade=True)

    def mark_incomplete(self, cascade=True):
        """Mark task as incomplete and cascade to parent if needed"""
        self.completed = False
        self.completed_at = None

        # Cascade up: if this task becomes incomplete,
        # parent should also be incomplete
        if cascade and self.parent and self.parent.completed:
            self.parent.mark_incomplete(cascade=False)

    def is_ancestor_of(self, other_task):
        """Check if this task is an ancestor of another task"""
        current = other_task.parent
        while current:
            if current.id == self.id:
                return True
            current = current.parent
        return False

    def get_all_descendants(self):
        """Get all descendant tasks (children, grandchildren, etc.)"""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def to_dict(self, include_children=False):
        """Convert task to dictionary, optionally include children"""
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "urgency": self.urgency,
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "user_id": self.user_id,
            "list_id": self.list_id,
            "parent_id": self.parent_id,
            "depth": self.get_depth(),
        }

        if include_children:
            result["children"] = [
                child.to_dict(include_children=True) for child in self.children
            ]

        return result
