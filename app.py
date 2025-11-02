"""
Hierarchical Todo List App - Flask Backend
==========================================

This is the main Flask application file that serves as our API backend.
The React frontend will communicate with this Flask app through HTTP requests.

Key Components:
- Flask app with CORS enabled (allows React to call our API)
- SQLAlchemy for database operations
- Flask-Login for user authentication
- Environment-based configuration
"""

from flask import Flask, jsonify
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import our models and routes
from backend.models import db, User, TodoList, Task
from backend.auth import auth_bp
from backend.api import api_bp

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
# Regular Flask app (no static serving)
app = Flask(__name__)

# ========================================
# CONFIGURATION
# ========================================

# Secret key for session management and security
# In production, this should be a random, secure string
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)

# Database configuration
# SQLite database will be stored in instance/todo_app.db
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///todo_app.db"
)
# Disable event notifications to save memory
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ========================================
# INITIALIZE EXTENSIONS
# ========================================

# Enable CORS with credentials for cross-origin cookie support
CORS(
    app,
    origins=["http://localhost:3000"],  # React dev server
    supports_credentials=True,  # Enable cookies in cross-origin requests
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize database with app
db.init_app(app)

# Initialize user authentication manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # Redirect to blueprint login route

# ========================================
# SERVE REACT APP
# ========================================

# ========================================
# REGISTER BLUEPRINTS
# ========================================

# Register authentication routes
app.register_blueprint(auth_bp, url_prefix="/api")

# Register CRUD API routes
app.register_blueprint(api_bp, url_prefix="/api")

# ========================================
# USER LOADER FUNCTION
# ========================================


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login requires this function to reload a user from the user ID
    stored in the session. Now implemented with our User model.
    """
    return User.query.get(int(user_id))


# ========================================
# TEST ROUTES
# ========================================


@app.route("/")
def home():
    """
    Basic route to test if our Flask app is working.
    This will return a simple JSON response.
    """
    return jsonify(
        {
            "message": "Hierarchical Todo List API is running!",
            "status": "success",
            "endpoints": [
                "/api/register - User registration",
                "/api/login - User login",
                "/api/logout - User logout",
                "/api/lists - Todo lists management",
                "/api/tasks - Tasks management",
            ],
        }
    )


@app.route("/api/health")
def health_check():
    """
    Health check endpoint to verify API is responding.
    Useful for testing and monitoring.
    """
    return jsonify(
        {"status": "healthy", "database": "connected" if db.engine else "disconnected"}
    )


# ========================================
# DATABASE INITIALIZATION
# ========================================


def create_tables():
    """
    Create all database tables.
    This will be called when we run the app for the first time.
    """
    with app.app_context():
        db.create_all()
        # Database tables created successfully - logged for development tracking


# ========================================
# MAIN APPLICATION RUNNER
# ========================================


if __name__ == "__main__":
    # Create database tables if they don't exist
    create_tables()

    # Run the Flask development server
    # debug=True enables auto-reload when code changes
    # host='0.0.0.0' makes the server accessible from other devices
    app.run(debug=True, host="0.0.0.0", port=5001)
