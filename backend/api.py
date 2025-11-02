"""
CRUD API Routes for Lists and Tasks
==================================

This module handles Create, Read, Update, Delete operations for:
- TodoLists: User's collections of tasks
- Tasks: Individual todo items (basic CRUD, hierarchy in next step)
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import db, TodoList, Task

# Create API blueprint
api_bp = Blueprint("api", __name__)



@api_bp.route("/lists", methods=["GET"])
@login_required
def get_lists():
    """Get all lists for the current user"""
    lists = TodoList.query.filter_by(user_id=current_user.id).all()
    return jsonify({"lists": [todo_list.to_dict() for todo_list in lists]})


@api_bp.route("/lists/<int:list_id>", methods=["GET"])
@login_required
def get_list(list_id):
    """Get a specific list with all its tasks"""
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first()

    if not todo_list:
        return jsonify({"error": "List not found"}), 404

    return jsonify({"list": todo_list.to_dict(include_tasks=True)})


@api_bp.route("/lists", methods=["POST"])
@login_required
def create_list():
    """Create a new todo list"""
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "List name is required"}), 400

    name = data["name"].strip()
    if not name:
        return jsonify({"error": "List name cannot be empty"}), 400

    # Create new list
    todo_list = TodoList(
        name=name, description=data.get("description", ""), user_id=current_user.id
    )

    try:
        db.session.add(todo_list)
        db.session.commit()

        return (
            jsonify(
                {"message": "List created successfully", "list": todo_list.to_dict()}
            ),
            201,
        )

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create list"}), 500


@api_bp.route("/lists/<int:list_id>", methods=["PUT"])
@login_required
def update_list(list_id):
    """Update an existing list"""
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first()

    if not todo_list:
        return jsonify({"error": "List not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update fields if provided
    if "name" in data:
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "List name cannot be empty"}), 400
        todo_list.name = name

    if "description" in data:
        todo_list.description = data["description"]

    try:
        db.session.commit()
        return jsonify(
            {"message": "List updated successfully", "list": todo_list.to_dict()}
        )

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update list"}), 500


@api_bp.route("/lists/<int:list_id>", methods=["DELETE"])
@login_required
def delete_list(list_id):
    """Delete a list and all its tasks"""
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first()

    if not todo_list:
        return jsonify({"error": "List not found"}), 404

    try:
        # SQLAlchemy will cascade delete all tasks due to our model setup
        db.session.delete(todo_list)
        db.session.commit()

        return jsonify({"message": "List deleted successfully"})

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete list"}), 500


# ========================================
# TASKS ENDPOINTS (Basic CRUD)
# ========================================


@api_bp.route("/tasks/<int:list_id>", methods=["GET"])
@login_required
def get_tasks(list_id):
    """Get all tasks in a specific list"""
    # Verify user owns the list
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first()

    if not todo_list:
        return jsonify({"error": "List not found"}), 404

    # Get only top-level tasks (no parent) - hierarchy handled in Step 5
    tasks = Task.query.filter_by(
        list_id=list_id, user_id=current_user.id, parent_id=None
    ).all()

    return jsonify({"tasks": [task.to_dict(include_children=True) for task in tasks]})


@api_bp.route("/task/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    """Get details of a specific task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"task": task.to_dict(include_children=True)})


@api_bp.route("/tasks", methods=["POST"])
@login_required
def create_task():
    """Create a new task"""
    data = request.get_json()

    if not data or not all(k in data for k in ("title", "list_id")):
        return jsonify({"error": "Title and list_id are required"}), 400

    list_id = data["list_id"]
    title = data["title"].strip()

    if not title:
        return jsonify({"error": "Task title cannot be empty"}), 400

    # Verify user owns the list
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first()

    if not todo_list:
        return jsonify({"error": "List not found"}), 404

    # Create new task
    task = Task(
        title=title,
        description=data.get("description", ""),
        urgency=data.get("urgency", "medium"),
        list_id=list_id,
        user_id=current_user.id,
        parent_id=data.get("parent_id"),  # For hierarchy (Step 5)
    )

    try:
        db.session.add(task)
        db.session.commit()

        return (
            jsonify({"message": "Task created successfully", "task": task.to_dict()}),
            201,
        )

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create task"}), 500


@api_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    """Update an existing task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update fields if provided
    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"error": "Task title cannot be empty"}), 400
        task.title = title

    if "description" in data:
        task.description = data["description"]

    if "urgency" in data:
        valid_urgencies = ["low", "medium", "high", "urgent"]
        if data["urgency"] in valid_urgencies:
            task.urgency = data["urgency"]

    if "completed" in data:
        if data["completed"]:
            task.mark_completed()
        else:
            task.mark_incomplete()

    try:
        db.session.commit()
        return jsonify({"message": "Task updated successfully", "task": task.to_dict()})

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update task"}), 500


@api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    """Delete a task and all its subtasks"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    try:
        # SQLAlchemy will cascade delete all subtasks due to our model setup
        db.session.delete(task)
        db.session.commit()

        return jsonify({"message": "Task deleted successfully"})

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete task"}), 500


# ========================================
# HIERARCHICAL TASK ENDPOINTS
# ========================================


@api_bp.route("/tasks/<int:parent_id>/subtasks", methods=["POST"])
@login_required
def create_subtask(parent_id):
    """Create a subtask under a specific parent task"""
    parent_task = Task.query.filter_by(id=parent_id, user_id=current_user.id).first()

    if not parent_task:
        return jsonify({"error": "Parent task not found"}), 404

    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    title = data["title"].strip()
    if not title:
        return jsonify({"error": "Task title cannot be empty"}), 400

    # Check depth limit (prevent infinite nesting)
    if parent_task.get_depth() >= 5:  # Max 5 levels deep
        return jsonify({"error": "Maximum nesting depth reached"}), 400

    # Create subtask
    subtask = Task(
        title=title,
        description=data.get("description", ""),
        urgency=data.get("urgency", "medium"),
        list_id=parent_task.list_id,
        user_id=current_user.id,
        parent_id=parent_id,
    )

    try:
        db.session.add(subtask)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Subtask created successfully",
                    "task": subtask.to_dict(),
                    "parent": parent_task.to_dict(include_children=True),
                }
            ),
            201,
        )

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create subtask"}), 500


@api_bp.route("/tasks/<int:task_id>/subtasks", methods=["GET"])
@login_required
def get_subtasks(task_id):
    """Get all direct children of a specific task"""
    parent_task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not parent_task:
        return jsonify({"error": "Task not found"}), 404

    # Get direct children only
    subtasks = Task.query.filter_by(parent_id=task_id, user_id=current_user.id).all()

    return jsonify(
        {
            "parent": parent_task.to_dict(),
            "subtasks": [task.to_dict(include_children=True) for task in subtasks],
        }
    )


@api_bp.route("/tasks/<int:task_id>/move", methods=["PUT"])
@login_required
def move_task(task_id):
    """Move a task to a different parent or make it top-level"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    new_parent_id = data.get("parent_id")  # None means make it top-level

    # Validate new parent if provided
    if new_parent_id is not None:
        new_parent = Task.query.filter_by(
            id=new_parent_id, user_id=current_user.id
        ).first()

        if not new_parent:
            return jsonify({"error": "New parent task not found"}), 404

        # Prevent moving task to its own descendant (would create cycle)
        if task.is_ancestor_of(new_parent):
            return jsonify({"error": "Cannot move task to descendant"}), 400

        # Check depth limit
        if new_parent.get_depth() >= 5:
            return jsonify({"error": "Maximum nesting depth reached"}), 400

        # Ensure both tasks are in the same list
        if task.list_id != new_parent.list_id:
            return jsonify({"error": "Cannot move task to different list"}), 400

    try:
        task.parent_id = new_parent_id
        db.session.commit()

        return jsonify(
            {
                "message": "Task moved successfully",
                "task": task.to_dict(include_children=True),
            }
        )

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to move task"}), 500


@api_bp.route("/tasks/<int:task_id>/tree", methods=["GET"])
@login_required
def get_task_tree(task_id):
    """Get complete tree structure starting from a specific task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(
        {
            "tree": task.to_dict(include_children=True),
            "depth": task.get_depth(),
            "total_descendants": len(task.get_all_descendants()),
        }
    )


@api_bp.route("/tasks/<int:task_id>/flatten", methods=["GET"])
@login_required
def flatten_task_tree(task_id):
    """Get a flat list of all tasks in a tree (useful for search/filtering)"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Get all descendants in a flat structure
    all_tasks = [task] + task.get_all_descendants()

    return jsonify(
        {
            "tasks": [t.to_dict() for t in all_tasks],
            "total_count": len(all_tasks),
            "completed_count": len([t for t in all_tasks if t.completed]),
        }
    )


# ========================================
# TASK MANAGEMENT ENDPOINTS
# ========================================


@api_bp.route("/tasks/<int:task_id>/move-to-list", methods=["PUT"])
@login_required
def move_task_to_list(task_id):
    """Move a top-level task to a different list"""
    data = request.get_json()

    if not data or "new_list_id" not in data:
        return jsonify({"error": "new_list_id is required"}), 400

    new_list_id = data["new_list_id"]

    # Get the task to move (must be owned by current user)
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Check if task is top-level (no parent)
    if task.parent_id is not None:
        return (
            jsonify({"error": "Only top-level tasks can be moved between lists"}),
            400,
        )

    # Get the destination list (must be owned by current user)
    new_list = TodoList.query.filter_by(id=new_list_id, user_id=current_user.id).first()
    if not new_list:
        return jsonify({"error": "Destination list not found"}), 404

    try:
        # Helper function to recursively update list_id for all descendants
        def update_descendants_list_id(parent_task, new_list_id):
            """Recursively update list_id for a task and all its descendants"""
            parent_task.list_id = new_list_id
            for child in parent_task.children:
                update_descendants_list_id(child, new_list_id)

        # Update the task and all its children's list_id
        update_descendants_list_id(task, new_list_id)
        db.session.commit()

        return jsonify(
            {
                "message": "Task moved successfully",
                "task": task.to_dict(include_children=True),
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to move task: {str(e)}"}), 500


# ========================================
# BULK TASK OPERATIONS
# ========================================


@api_bp.route("/lists/<int:list_id>/complete-all", methods=["PUT"])
@login_required
def complete_all_tasks(list_id):
    """Mark all tasks in a list as completed"""
    # Verify the list belongs to the user
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first()
    if not todo_list:
        return jsonify({"error": "List not found"}), 404

    try:
        # Get all top-level tasks in the list
        top_level_tasks = Task.query.filter_by(
            list_id=list_id, user_id=current_user.id, parent_id=None
        ).all()

        # Mark each top-level task as completed (will cascade to children)
        for task in top_level_tasks:
            if not task.completed:
                task.mark_completed(cascade=True)

        db.session.commit()

        return jsonify({"message": "All tasks completed successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to complete all tasks: {str(e)}"}), 500


@api_bp.route("/lists/<int:list_id>/uncheck-all", methods=["PUT"])
@login_required
def uncheck_all_tasks(list_id):
    """Mark all tasks in a list as incomplete"""
    # Verify the list belongs to the user
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first()
    if not todo_list:
        return jsonify({"error": "List not found"}), 404

    try:
        # Get all tasks in the list (both top-level and children)
        all_tasks = Task.query.filter_by(list_id=list_id, user_id=current_user.id).all()

        # Mark all tasks as incomplete directly (no cascading logic needed)
        for task in all_tasks:
            task.completed = False
            task.completed_at = None

        db.session.commit()

        return jsonify({"message": "All tasks unchecked successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to uncheck all tasks: {str(e)}"}), 500
