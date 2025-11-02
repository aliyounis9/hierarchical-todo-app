# 📋 Hierarchical Todo App

## Overview
A full-stack hierarchical todo application built with Flask (backend) and React (frontend). This application allows users to create, organize, and manage tasks in a hierarchical structure with support for subtasks, multiple urgency levels, and collaborative list management.

## Features

### 🔐 **Authentication System**
- User registration and login
- Session-based authentication
- Protected routes and API endpoints

### 📝 **Todo List Management**
- Create, read, update, and delete todo lists
- Edit list names and descriptions
- Multiple lists per user

### 📋 **Hierarchical Task System**
- Create parent tasks and unlimited levels of subtasks
- Nested task organization
- Cascading completion (completing parent completes all children)

### 🎯 **Task Features**
- Four urgency levels: Low, Medium, High, Urgent
- Color-coded urgency indicators
- Task completion tracking
- Move tasks between lists
- Bulk operations (complete all/uncheck all tasks in a list)

### 🧪 **Comprehensive Testing**
- **100% test coverage** (47/47 tests passing)
- Unit tests for models and business logic
- Integration tests for complete workflows
- API endpoint testing
- Authentication and authorization testing

### 🎨 **Clean UI Design**
- Minimal, distraction-free interface
- Custom todo clipboard icon for professional branding
- Responsive design that works on all devices

## Tech Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User session management
- **SQLite** - Database
- **pytest** - Testing framework

### Frontend
- **React** - JavaScript UI library
- **React Router** - Client-side routing
- **CSS3** - Styling with responsive design
- **Fetch API** - HTTP client

## Project Structure
```
hierarchical-todo-app/
├── .gitignore             # Git ignore configuration
├── README.md              # Project documentation
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── backend/
│   ├── __init__.py       # Python package marker
│   ├── models.py         # Database models (User, TodoList, Task)
│   ├── api.py            # API routes and endpoints
│   └── auth.py           # Authentication routes
├── frontend/
│   ├── package.json      # Node.js dependencies and scripts
│   ├── package-lock.json # Locked dependency versions
│   ├── public/           # Static assets
│   │   ├── index.html    # Main HTML template
│   │   ├── icon.svg      # Custom todo app icon
│   │   └── manifest.json # Web app manifest
│   └── src/
│       ├── App.js        # Main React application
│       ├── App.css       # Application styles
│       ├── api.js        # API utility functions
│       ├── index.js      # React entry point
│       ├── index.css     # Global styles
│       └── components/   # React components
│           ├── AuthForm.js      # Login/Register component
│           ├── Dashboard.js     # Main dashboard component
│           ├── Task.js          # Individual task component
│           └── TaskList.js      # Task list component
└── tests/
    ├── __init__.py       # Python package marker
    ├── conftest.py       # Test configuration and fixtures
    ├── test_models.py    # Model unit tests
    ├── test_api.py       # API endpoint tests
    ├── test_auth.py      # Authentication tests
    └── test_integration.py # Integration tests
```

**Note:** This structure shows only source code files tracked by git. Generated files like `node_modules/`, `build/`, `__pycache__/`, `instance/`, and `.env` are excluded by the `.gitignore` file.

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup
1. **Navigate to the project directory:**
   ```bash
   cd hierarchical-todo-app
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup
1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

## Running the Application

1. **Start the Flask backend** (in the main directory):
   ```bash
   python app.py
   ```
   Backend will run on: http://localhost:5001

2. **Start the React frontend** (in a new terminal, from the `frontend/` directory):
   ```bash
   npm start
   ```
   Frontend will run on: http://localhost:3000

3. **Access the application:**
   Open your browser to http://localhost:3000

**Note:** This application is configured for development with separate frontend and backend servers. The Flask server serves only the API endpoints, while React handles the user interface.

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_models.py      # Model tests
python -m pytest tests/test_api.py         # API tests
python -m pytest tests/test_auth.py        # Authentication tests
python -m pytest tests/test_integration.py # Integration tests

# Run with coverage report
python -m pytest tests/ --cov=backend
```

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### Todo Lists
- `GET /api/lists` - Get all user's lists
- `POST /api/lists` - Create new list
- `GET /api/lists/:id` - Get specific list
- `PUT /api/lists/:id` - Update list
- `DELETE /api/lists/:id` - Delete list

### Tasks
- `GET /api/tasks/:listId` - Get tasks for a list
- `POST /api/tasks` - Create new task
- `POST /api/tasks/:id/subtasks` - Create subtask
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `PUT /api/tasks/:id/move-to-list` - Move task to different list

### Bulk Operations
- `PUT /api/lists/:id/complete-all` - Mark all tasks complete
- `PUT /api/lists/:id/uncheck-all` - Mark all tasks incomplete

## Usage

1. **Register/Login:** Create an account or log in to an existing one
2. **Create Lists:** Add todo lists for different projects or categories
3. **Add Tasks:** Create tasks within your lists
4. **Create Subtasks:** Break down complex tasks into smaller subtasks
5. **Set Urgency:** Assign urgency levels to prioritize your work
6. **Organize:** Move tasks between lists as needed
7. **Track Progress:** Check off completed tasks and see progress

## Development Features

- **Hot Reload:** Both frontend and backend support hot reloading during development
- **Error Handling:** Comprehensive error handling with user-friendly messages
- **Responsive Design:** Works on desktop and mobile devices
- **Session Persistence:** User sessions persist across browser refreshes

## Contributing

This project demonstrates full-stack web development principles including:
- RESTful API design
- React component architecture
- Database modeling and relationships
- User authentication and authorization
- Comprehensive testing strategies
- Modern development workflows

## License

This project is created for educational purposes as part of CS162 coursework.