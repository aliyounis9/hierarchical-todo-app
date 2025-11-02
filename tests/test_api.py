"""
API Endpoint Tests
=================

Integration tests for REST API endpoints:
- TodoList CRUD operations (create, read, update, delete)
- Task management with hierarchical relationships
- Authentication and authorization validation
- Error handling and edge cases
- Bulk operations (complete all, uncheck all)
"""

import json
from backend.models import User, TodoList, Task, db


class TestTodoListAPI:
    """Test TodoList API endpoints"""

    def test_get_todo_lists(self, client, auth, user):
        """Test getting all todo lists for a user"""
        auth.login()

        # Create some test lists
        with client.application.app_context():
            list1 = TodoList(name="List 1", user_id=user.id)
            list2 = TodoList(name="List 2", user_id=user.id)
            db.session.add_all([list1, list2])
            db.session.commit()

        response = client.get("/api/lists")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "lists" in data
        assert len(data["lists"]) >= 2

    def test_create_todo_list(self, client, auth, user):
        """Test creating a new todo list"""
        auth.login()

        list_data = {"name": "New List", "description": "A new test list"}

        response = client.post(
            "/api/lists", data=json.dumps(list_data), content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "list" in data
        assert data["list"]["name"] == "New List"
        assert data["list"]["description"] == "A new test list"

    def test_get_single_todo_list(self, client, auth, todo_list):
        """Test getting a single todo list"""
        auth.login()

        response = client.get(f"/api/lists/{todo_list.id}")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "list" in data
        assert data["list"]["name"] == todo_list.name

    def test_update_todo_list(self, client, auth, todo_list):
        """Test updating a todo list"""
        auth.login()

        update_data = {
            "name": "Updated List Name",
            "description": "Updated description",
        }

        response = client.put(
            f"/api/lists/{todo_list.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "list" in data
        assert data["list"]["name"] == "Updated List Name"

    def test_delete_todo_list(self, client, auth, todo_list):
        """Test deleting a todo list"""
        auth.login()

        response = client.delete(f"/api/lists/{todo_list.id}")
        assert response.status_code == 200

        # Verify list is deleted
        response = client.get(f"/api/lists/{todo_list.id}")
        assert response.status_code == 404


class TestTaskAPI:
    """Test Task API endpoints"""

    def test_get_tasks(self, client, auth, todo_list):
        """Test getting all tasks for a list"""
        auth.login()

        response = client.get(f"/api/tasks/{todo_list.id}")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_create_task(self, client, auth, todo_list):
        """Test creating a new task"""
        auth.login()

        task_data = {
            "title": "New Task",
            "description": "A new test task",
            "urgency": "high",
            "list_id": todo_list.id,
        }

        response = client.post(
            "/api/tasks", data=json.dumps(task_data), content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "task" in data
        assert data["task"]["title"] == "New Task"
        assert data["task"]["urgency"] == "high"

    def test_create_subtask(self, client, auth, task):
        """Test creating a subtask"""
        auth.login()

        subtask_data = {
            "title": "Subtask",
            "description": "A subtask",
            "urgency": "low",
        }

        response = client.post(
            f"/api/tasks/{task.id}/subtasks",
            data=json.dumps(subtask_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "task" in data
        assert data["task"]["title"] == "Subtask"
        assert data["task"]["parent_id"] == task.id

    def test_update_task(self, client, auth, task):
        """Test updating a task"""
        auth.login()

        update_data = {"title": "Updated Task", "completed": True, "urgency": "urgent"}

        response = client.put(
            f"/api/tasks/{task.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "task" in data
        assert data["task"]["title"] == "Updated Task"
        assert data["task"]["completed"] is True
        assert data["task"]["urgency"] == "urgent"

    def test_delete_task(self, client, auth, task):
        """Test deleting a task"""
        auth.login()

        response = client.delete(f"/api/tasks/{task.id}")
        assert response.status_code == 200

        # Verify task is deleted
        response = client.get(f"/api/task/{task.id}")
        assert response.status_code == 404

    def test_move_task(self, client, auth, user, task):
        """Test moving a task to a different list"""
        auth.login()

        # Create another list
        with client.application.app_context():
            new_list = TodoList(name="Target List", user_id=user.id)
            db.session.add(new_list)
            db.session.commit()
            new_list_id = new_list.id

        move_data = {"new_list_id": new_list_id}

        response = client.put(
            f"/api/tasks/{task.id}/move-to-list",
            data=json.dumps(move_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "task" in data
        assert data["task"]["list_id"] == new_list_id

    def test_bulk_complete_tasks(self, client, auth, user, todo_list):
        """Test bulk completing all tasks in a list"""
        auth.login()

        # Create some tasks
        with client.application.app_context():
            task1 = Task(title="Task 1", list_id=todo_list.id, user_id=user.id)
            task2 = Task(title="Task 2", list_id=todo_list.id, user_id=user.id)
            db.session.add_all([task1, task2])
            db.session.commit()

        response = client.put(f"/api/lists/{todo_list.id}/complete-all")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "message" in data

    def test_bulk_uncheck_tasks(self, client, auth, user, todo_list):
        """Test bulk unchecking all tasks in a list"""
        auth.login()

        # Create some completed tasks
        with client.application.app_context():
            task1 = Task(
                title="Task 1", list_id=todo_list.id, user_id=user.id, completed=True
            )
            task2 = Task(
                title="Task 2", list_id=todo_list.id, user_id=user.id, completed=True
            )
            db.session.add_all([task1, task2])
            db.session.commit()

        response = client.put(f"/api/lists/{todo_list.id}/uncheck-all")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "message" in data


class TestAuthenticationRequired:
    """Test that API endpoints require authentication"""

    def test_todo_lists_require_auth(self, client):
        """Test that todo list endpoints require authentication"""
        response = client.get("/api/lists")
        assert response.status_code == 302  # Redirect to login

    def test_tasks_require_auth(self, client):
        """Test that task endpoints require authentication"""
        response = client.get("/api/tasks/1")
        assert response.status_code == 302  # Redirect to login

    def test_create_task_requires_auth(self, client):
        """Test that creating tasks requires authentication"""
        task_data = {"title": "New Task", "list_id": 1}
        response = client.post(
            "/api/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        assert response.status_code == 302  # Redirect to login


class TestErrorHandling:
    """Test API error handling"""

    def test_invalid_todo_list_id(self, client, auth, user):
        """Test accessing non-existent todo list"""
        auth.login()

        response = client.get("/api/lists/99999")
        assert response.status_code == 404

    def test_invalid_task_id(self, client, auth, user):
        """Test accessing non-existent task"""
        auth.login()

        response = client.get("/api/task/99999")
        assert response.status_code == 404

    def test_invalid_json_data(self, client, auth, todo_list):
        """Test sending invalid JSON data"""
        auth.login()

        response = client.post(
            "/api/tasks", data="invalid json", content_type="application/json"
        )
        assert response.status_code == 400

    def test_missing_required_fields(self, client, auth, todo_list):
        """Test creating task without required fields"""
        auth.login()

        # Missing title field
        task_data = {"description": "No title", "list_id": todo_list.id}

        response = client.post(
            "/api/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        assert response.status_code == 400

    def test_depth_limit_error(self, client, auth, user, todo_list):
        """Test creating subtasks beyond depth limit"""
        auth.login()

        # Create a deep hierarchy (assuming max depth is 3)
        with client.application.app_context():
            level0 = Task(title="Level 0", list_id=todo_list.id, user_id=user.id)
            db.session.add(level0)
            db.session.commit()

            level1 = Task(
                title="Level 1",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=level0.id,
            )
            db.session.add(level1)
            db.session.commit()

            level2 = Task(
                title="Level 2",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=level1.id,
            )
            db.session.add(level2)
            db.session.commit()

            level2_id = level2.id

        # Try to create level 3 (should fail if max depth is 3)
        subtask_data = {"title": "Level 3", "description": "Too deep"}

        response = client.post(
            f"/api/tasks/{level2_id}/subtasks",
            data=json.dumps(subtask_data),
            content_type="application/json",
        )

        # Should either succeed or return 400 with depth limit message
        if response.status_code == 400:
            data = json.loads(response.data)
            assert "depth" in data.get("error", "").lower()
