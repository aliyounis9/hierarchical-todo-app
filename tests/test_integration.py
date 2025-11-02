"""
Integration Tests
================

End-to-end integration tests covering complete user workflows:
- Full user journey from registration to task management
- Multi-list and multi-task scenarios
- Complex hierarchical task operations
- Cross-feature interactions and data consistency
- Real-world usage patterns
"""

import json
from backend.models import User, TodoList, Task, db


class TestUserWorkflow:
    """Test complete user workflows"""

    def test_complete_user_workflow(self, client, app):
        """Test a complete user workflow from registration to task management"""
        # Register a new user
        user_data = {
            "username": "workflowuser",
            "email": "workflow@example.com",
            "password": "testpass123",
        }

        response = client.post(
            "/api/register", data=json.dumps(user_data), content_type="application/json"
        )
        assert response.status_code == 201

        # Login
        login_data = {"username": "workflow@example.com", "password": "testpass123"}

        response = client.post(
            "/api/login", data=json.dumps(login_data), content_type="application/json"
        )
        assert response.status_code == 200

        # Create a todo list
        list_data = {"name": "Work Projects", "description": "My work tasks"}

        response = client.post(
            "/api/lists", data=json.dumps(list_data), content_type="application/json"
        )
        assert response.status_code == 201
        list_id = json.loads(response.data)["list"]["id"]

        # Create a parent task
        task_data = {
            "title": "Complete Project",
            "description": "Main project task",
            "urgency": "high",
            "list_id": list_id,
        }

        response = client.post(
            "/api/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        assert response.status_code == 201
        parent_task_id = json.loads(response.data)["task"]["id"]

        # Create subtasks
        subtask1_data = {
            "title": "Design Phase",
            "description": "Create mockups",
            "urgency": "medium",
        }

        response = client.post(
            f"/api/tasks/{parent_task_id}/subtasks",
            data=json.dumps(subtask1_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        subtask2_data = {
            "title": "Development Phase",
            "description": "Write code",
            "urgency": "high",
        }

        response = client.post(
            f"/api/tasks/{parent_task_id}/subtasks",
            data=json.dumps(subtask2_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Get all tasks to verify hierarchy
        response = client.get(f"/api/tasks/{list_id}")
        assert response.status_code == 200

        tasks = json.loads(response.data)["tasks"]

        # Count all tasks (parent + children)
        def count_all_tasks(task_list):
            count = 0
            for task in task_list:
                count += 1  # Count the task itself
                if "children" in task:
                    count += count_all_tasks(
                        task["children"]
                    )  # Count children recursively
            return count

        total_tasks = count_all_tasks(tasks)
        assert total_tasks >= 3  # Parent + 2 subtasks

        # Complete parent task (should cascade to children)
        update_data = {"completed": True}
        response = client.put(
            f"/api/tasks/{parent_task_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Verify all tasks are completed
        response = client.get(f"/api/tasks/{list_id}")
        tasks = json.loads(response.data)["tasks"]

        for task in tasks:
            if task["id"] == parent_task_id or task["parent_id"] == parent_task_id:
                assert task["completed"]

        # Logout
        response = client.post("/api/logout")
        assert response.status_code == 200


class TestTaskHierarchy:
    """Test task hierarchy functionality"""

    def test_deep_hierarchy_creation(self, client, auth, user, todo_list):
        """Test creating a deep task hierarchy"""
        auth.login()

        # Create root task
        root_data = {
            "title": "Root Task",
            "description": "Top level task",
            "urgency": "medium",
            "list_id": todo_list.id,
        }

        response = client.post(
            "/api/tasks", data=json.dumps(root_data), content_type="application/json"
        )
        assert response.status_code == 201
        root_id = json.loads(response.data)["task"]["id"]

        # Create level 1 subtask
        level1_data = {
            "title": "Level 1 Task",
            "description": "First level subtask",
            "urgency": "low",
        }

        response = client.post(
            f"/api/tasks/{root_id}/subtasks",
            data=json.dumps(level1_data),
            content_type="application/json",
        )
        assert response.status_code == 201
        level1_id = json.loads(response.data)["task"]["id"]

        # Create level 2 subtask
        level2_data = {
            "title": "Level 2 Task",
            "description": "Second level subtask",
            "urgency": "urgent",
        }

        response = client.post(
            f"/api/tasks/{level1_id}/subtasks",
            data=json.dumps(level2_data),
            content_type="application/json",
        )
        assert response.status_code == 201
        level2_id = json.loads(response.data)["task"]["id"]

        # Verify hierarchy
        response = client.get(f"/api/tasks/{todo_list.id}")
        tasks = json.loads(response.data)["tasks"]

        # Find tasks and verify relationships
        root_task = next(t for t in tasks if t["id"] == root_id)
        level1_task = next(t for t in root_task["children"] if t["id"] == level1_id)
        level2_task = next(t for t in level1_task["children"] if t["id"] == level2_id)

        assert root_task["parent_id"] is None
        assert level1_task["parent_id"] == root_id
        assert level2_task["parent_id"] == level1_id

    def test_cascading_completion_behavior(self, client, auth, user, todo_list):
        """Test cascading completion across multiple levels"""
        auth.login()

        # Create hierarchy: parent -> child1, child2 -> grandchild
        with client.application.app_context():
            parent = Task(title="Parent", list_id=todo_list.id, user_id=user.id)
            db.session.add(parent)
            db.session.commit()

            child1 = Task(
                title="Child 1",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=parent.id,
            )
            child2 = Task(
                title="Child 2",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=parent.id,
            )
            db.session.add_all([child1, child2])
            db.session.commit()

            grandchild = Task(
                title="Grandchild",
                list_id=todo_list.id,
                user_id=user.id,
                parent_id=child1.id,
            )
            db.session.add(grandchild)
            db.session.commit()

            parent_id = parent.id
            child1_id = child1.id
            child2_id = child2.id
            grandchild_id = grandchild.id

        # Complete parent task
        update_data = {"completed": True}
        response = client.put(
            f"/api/tasks/{parent_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Verify all descendants are completed
        response = client.get(f"/api/tasks/{todo_list.id}")
        tasks = json.loads(response.data)["tasks"]

        # Flatten hierarchical tasks for easier searching
        def flatten_tasks(task_list):
            result = {}
            for task in task_list:
                result[task["id"]] = task
                if "children" in task and task["children"]:
                    result.update(flatten_tasks(task["children"]))
            return result

        task_dict = flatten_tasks(tasks)

        assert task_dict[parent_id]["completed"]
        assert task_dict[child1_id]["completed"]
        assert task_dict[child2_id]["completed"]
        assert task_dict[grandchild_id]["completed"]


class TestBulkOperations:
    """Test bulk operations functionality"""

    def test_bulk_operations_workflow(self, client, auth, user, todo_list):
        """Test complete bulk operations workflow"""
        auth.login()

        # Create multiple tasks with different urgencies
        tasks_data = [
            {"title": "Urgent Task", "urgency": "urgent"},
            {"title": "High Priority", "urgency": "high"},
            {"title": "Medium Task", "urgency": "medium"},
            {"title": "Low Priority", "urgency": "low"},
        ]

        created_tasks = []
        for task_data in tasks_data:
            task_data["list_id"] = todo_list.id  # Add list_id to task data
            response = client.post(
                "/api/tasks",
                data=json.dumps(task_data),
                content_type="application/json",
            )
            assert response.status_code == 201
            created_tasks.append(json.loads(response.data)["task"])

        # Bulk complete all tasks
        response = client.put(f"/api/lists/{todo_list.id}/complete-all")
        assert response.status_code == 200

        # Verify all tasks are completed
        response = client.get(f"/api/tasks/{todo_list.id}")
        tasks = json.loads(response.data)["tasks"]

        # Flatten hierarchical tasks for easier searching
        def flatten_tasks(task_list):
            result = []
            for task in task_list:
                result.append(task)
                if "children" in task and task["children"]:
                    result.extend(flatten_tasks(task["children"]))
            return result

        flat_tasks = flatten_tasks(tasks)

        for task in flat_tasks:
            if task["id"] in [t["id"] for t in created_tasks]:
                assert task["completed"]

        # Bulk uncheck all tasks
        response = client.put(f"/api/lists/{todo_list.id}/uncheck-all")
        assert response.status_code == 200

        # Verify all tasks are unchecked
        response = client.get(f"/api/tasks/{todo_list.id}")
        tasks = json.loads(response.data)["tasks"]

        flat_tasks = flatten_tasks(tasks)

        for task in flat_tasks:
            if task["id"] in [t["id"] for t in created_tasks]:
                assert not task["completed"]


class TestTaskMovement:
    """Test task movement between lists"""

    def test_move_task_between_lists(self, client, auth, user):
        """Test moving tasks between different lists"""
        auth.login()

        # Create two lists
        list1_data = {"name": "Personal", "description": "Personal tasks"}
        response = client.post(
            "/api/lists", data=json.dumps(list1_data), content_type="application/json"
        )
        assert response.status_code == 201
        list1_id = json.loads(response.data)["list"]["id"]

        list2_data = {"name": "Work", "description": "Work tasks"}
        response = client.post(
            "/api/lists", data=json.dumps(list2_data), content_type="application/json"
        )
        assert response.status_code == 201
        list2_id = json.loads(response.data)["list"]["id"]

        # Create task in first list
        task_data = {
            "title": "Moveable Task",
            "description": "This task will be moved",
            "urgency": "medium",
            "list_id": list1_id,
        }

        response = client.post(
            "/api/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        assert response.status_code == 201
        task_id = json.loads(response.data)["task"]["id"]

        # Move task to second list
        move_data = {"new_list_id": list2_id}
        response = client.put(
            f"/api/tasks/{task_id}/move-to-list",
            data=json.dumps(move_data),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Verify task is in second list
        response = client.get(f"/api/tasks/{list2_id}")
        tasks = json.loads(response.data)["tasks"]

        moved_task = next((t for t in tasks if t["id"] == task_id), None)
        assert moved_task is not None
        assert moved_task["list_id"] == list2_id

        # Verify task is not in first list
        response = client.get(f"/api/tasks/{list1_id}")
        tasks = json.loads(response.data)["tasks"]

        old_task = next((t for t in tasks if t["id"] == task_id), None)
        assert old_task is None


class TestUrgencySystem:
    """Test urgency system functionality"""

    def test_urgency_levels_and_colors(self, client, auth, todo_list):
        """Test creating tasks with different urgency levels"""
        auth.login()

        urgency_levels = ["low", "medium", "high", "urgent"]

        for urgency in urgency_levels:
            task_data = {
                "title": f"{urgency.title()} Task",
                "description": f"A task with {urgency} urgency",
                "urgency": urgency,
            }

            task_data["list_id"] = todo_list.id  # Add list_id to task data
            response = client.post(
                "/api/tasks",
                data=json.dumps(task_data),
                content_type="application/json",
            )
            assert response.status_code == 201

            created_task = json.loads(response.data)["task"]
            assert created_task["urgency"] == urgency

        # Get all tasks and verify urgency levels
        response = client.get(f"/api/tasks/{todo_list.id}")
        tasks = json.loads(response.data)["tasks"]

        urgencies_found = [t["urgency"] for t in tasks]
        for urgency in urgency_levels:
            assert urgency in urgencies_found
