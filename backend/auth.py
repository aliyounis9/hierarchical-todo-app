"""
Authentication API Routes
========================

This module handles user authentication: registration, login, logout.
All routes return JSON responses for our React frontend.
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from backend.models import db, User

# Create authentication blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account"""
    data = request.get_json()

    # Validate required fields
    required_fields = ("username", "email", "password")
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Username, email, and password required"}), 400

    username = data["username"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    # Basic validation
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if "@" not in email:
        return jsonify({"error": "Invalid email format"}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()

        # Automatically log in the new user
        login_user(user)

        return (
            jsonify({"message": "Registration successful", "user": user.to_dict()}),
            201,
        )

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and create session"""
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "password")):
        return jsonify({"error": "Username and password required"}), 400

    username = data["username"].strip()
    password = data["password"]

    # Find user by username or email
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if user and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({"message": "Login successful", "user": user.to_dict()})
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """End user session - clear both Flask-Login and session data"""
    if current_user.is_authenticated:
        # Clear Flask-Login session
        logout_user()

        # Clear session data completely
        session.clear()
        session.permanent = False

        # Create response with browser cache clearing
        response = jsonify({"message": "Logout successful"})
        response.headers["Clear-Site-Data"] = '"cookies"'

        return response
    else:
        session.clear()
        response = jsonify({"message": "User was not logged in"})
        response.headers["Clear-Site-Data"] = '"cookies"'
        return response


@auth_bp.route("/current_user", methods=["GET"])
@login_required
def get_current_user():
    """Get current logged-in user information"""
    return jsonify({"user": current_user.to_dict()})


@auth_bp.route("/check_auth", methods=["GET"])
def check_auth():
    """Check if user is authenticated (no login required)"""
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "user": current_user.to_dict()})
    else:
        return jsonify({"authenticated": False})
