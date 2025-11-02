/**
 * API Utility Functions
 * ====================
 * 
 * Centralized API communication with Flask backend.
 * Provides organized methods for:
 * - User authentication (register, login, logout)
 * - Todo list management (CRUD operations)
 * - Task management (hierarchical CRUD operations)
 * 
 * Uses native fetch() with consistent error handling.
 */

// API base URL - points to our Flask backend
const API_BASE_URL = 'http://localhost:5001/api';

// Helper function to handle all API requests with consistent error handling
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    credentials: 'include', // Include cookies for session management
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }
    
    return data;
  } catch (error) {
    // Re-throw error for component-level handling
    throw error;
  }
};

// Authentication API calls
export const auth = {
  // Register new user
  register: async (username, email, password) => {
    return apiRequest('/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
  },

  // Login user
  login: async (username, password) => {
    return apiRequest('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  },

  // Logout user
  logout: async () => {
    return apiRequest('/logout', { method: 'POST' });
  },

  // Check if user is authenticated
  checkAuth: async () => {
    return apiRequest('/check_auth');
  },
};

// Lists API calls
export const lists = {
  // Get all user's lists
  getAll: async () => {
    return apiRequest('/lists');
  },

  // Get specific list with tasks
  getById: async (listId) => {
    return apiRequest(`/lists/${listId}`);
  },

  // Create new list
  create: async (name, description = '') => {
    return apiRequest('/lists', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    });
  },

  // Update existing list
  update: async (listId, updates) => {
    return apiRequest(`/lists/${listId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  // Delete list
  delete: async (listId) => {
    return apiRequest(`/lists/${listId}`, {
      method: 'DELETE',
    });
  },
};

// Tasks API calls
export const tasks = {
  // Get all tasks in a list
  getByList: async (listId) => {
    return apiRequest(`/tasks/${listId}`);
  },

  // Get specific task
  getById: async (taskId) => {
    return apiRequest(`/task/${taskId}`);
  },

  // Create new task
  create: async (taskData) => {
    return apiRequest('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  },

  // Update existing task
  update: async (taskId, updates) => {
    return apiRequest(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  // Delete task
  delete: async (taskId) => {
    return apiRequest(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  },

  // Hierarchical task operations
  createSubtask: async (parentId, taskData) => {
    return apiRequest(`/tasks/${parentId}/subtasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  },

  getSubtasks: async (taskId) => {
    return apiRequest(`/tasks/${taskId}/subtasks`);
  },

  move: async (taskId, newParentId) => {
    return apiRequest(`/tasks/${taskId}/move`, {
      method: 'PUT',
      body: JSON.stringify({ parent_id: newParentId }),
    });
  },

  // Move task to different list (only for top-level tasks)
  moveToList: async (taskId, newListId) => {
    return apiRequest(`/tasks/${taskId}/move-to-list`, {
      method: 'PUT',
      body: JSON.stringify({ new_list_id: newListId }),
    });
  },

  getTree: async (taskId) => {
    return apiRequest(`/tasks/${taskId}/tree`);
  },

  getFlatten: async (taskId) => {
    return apiRequest(`/tasks/${taskId}/flatten`);
  },

  // Complete all tasks in a list
  completeAll: async (listId) => {
    return apiRequest(`/lists/${listId}/complete-all`, {
      method: 'PUT',
    });
  },

  // Uncheck all tasks in a list
  uncheckAll: async (listId) => {
    return apiRequest(`/lists/${listId}/uncheck-all`, {
      method: 'PUT',
    });
  },
};