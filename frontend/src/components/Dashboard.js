/**
 * Dashboard Component
 * ==================
 * 
 * Main user interface for managing todo lists:
 * - Display all user's todo lists
 * - Create, edit, and delete lists
 * - Navigate to individual list views
 * - Provide logout functionality
 */

import React, { useState, useEffect } from 'react';
import { lists, auth } from '../api';

const Dashboard = ({ user, onSelectList, onLogout }) => {
  const [userLists, setUserLists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAddList, setShowAddList] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [newListDescription, setNewListDescription] = useState('');
  const [editingList, setEditingList] = useState(null);
  const [editListName, setEditListName] = useState('');
  const [editListDescription, setEditListDescription] = useState('');

  // Load user's lists
  const loadLists = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await lists.getAll();
      setUserLists(response.lists);
    } catch (error) {
      setError('Failed to load lists: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Load lists when component mounts
  useEffect(() => {
    loadLists();
  }, []);

  // Handle user logout with error handling
  const handleLogout = async () => {
    try {
      await auth.logout();
    } catch (error) {
      // Silently handle logout API errors - user will be logged out locally
    }
    // Always call onLogout to clear local authentication state
    onLogout();
  };

  // Add new list
  const handleAddList = async () => {
    if (!newListName.trim()) return;

    setLoading(true);
    try {
      await lists.create(newListName, newListDescription);
      setNewListName('');
      setNewListDescription('');
      setShowAddList(false);
      loadLists(); // Refresh the lists
    } catch (error) {
      setError('Failed to create list: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Delete list
  const handleDeleteList = async (listId) => {
    if (window.confirm('Are you sure you want to delete this list and all its tasks?')) {
      setLoading(true);
      try {
        await lists.delete(listId);
        loadLists(); // Refresh the lists
      } catch (error) {
        setError('Failed to delete list: ' + error.message);
      } finally {
        setLoading(false);
      }
    }
  };

  // Start editing a list
  const handleStartEdit = (list) => {
    setEditingList(list.id);
    setEditListName(list.name);
    setEditListDescription(list.description || '');
  };

  // Cancel editing
  const handleCancelEdit = () => {
    setEditingList(null);
    setEditListName('');
    setEditListDescription('');
  };

  // Save list edits
  const handleSaveEdit = async () => {
    if (!editListName.trim()) return;

    setLoading(true);
    try {
      await lists.update(editingList, {
        name: editListName,
        description: editListDescription
      });
      setEditingList(null);
      setEditListName('');
      setEditListDescription('');
      loadLists(); // Refresh the lists
    } catch (error) {
      setError('Failed to update list: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>📋 Todo Lists Dashboard</h1>
        <div className="user-info">
          <span>Welcome, {user.username}!</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError('')}>×</button>
        </div>
      )}

      {/* Add new list section */}
      <div className="add-list-section">
        {!showAddList ? (
          <button 
            onClick={() => setShowAddList(true)}
            className="add-list-btn"
            disabled={loading}
          >
            + Create New List
          </button>
        ) : (
          <div className="add-list-form">
            <h3>Create New List</h3>
            <input
              type="text"
              value={newListName}
              onChange={(e) => setNewListName(e.target.value)}
              placeholder="List name..."
              className="list-name-input"
              disabled={loading}
            />
            <textarea
              value={newListDescription}
              onChange={(e) => setNewListDescription(e.target.value)}
              placeholder="List description (optional)..."
              className="list-description-input"
              disabled={loading}
            />
            <div className="form-buttons">
              <button 
                onClick={handleAddList}
                disabled={loading || !newListName.trim()}
              >
                Create List
              </button>
              <button 
                onClick={() => {
                  setShowAddList(false);
                  setNewListName('');
                  setNewListDescription('');
                }}
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Lists display */}
      <div className="lists-container">
        {loading && userLists.length === 0 ? (
          <div className="loading">Loading your lists...</div>
        ) : userLists.length === 0 ? (
          <div className="no-lists">
            <p>You don't have any lists yet.</p>
            <p>Create your first list to get started!</p>
          </div>
        ) : (
          <div className="lists-grid">
            {userLists.map((list) => (
              <div key={list.id} className="list-card">
                {editingList === list.id ? (
                  // Edit mode
                  <div className="edit-list-form">
                    <input
                      type="text"
                      value={editListName}
                      onChange={(e) => setEditListName(e.target.value)}
                      placeholder="List name..."
                      className="edit-list-name-input"
                      disabled={loading}
                    />
                    <textarea
                      value={editListDescription}
                      onChange={(e) => setEditListDescription(e.target.value)}
                      placeholder="List description (optional)..."
                      className="edit-list-description-input"
                      disabled={loading}
                    />
                    <div className="edit-form-buttons">
                      <button 
                        onClick={handleSaveEdit}
                        disabled={loading || !editListName.trim()}
                        className="save-edit-btn"
                      >
                        Save
                      </button>
                      <button 
                        onClick={handleCancelEdit}
                        disabled={loading}
                        className="cancel-edit-btn"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // Display mode
                  <>
                    <div className="list-header">
                      <h3 className="list-title">{list.name}</h3>
                      <div className="list-actions">
                        <button
                          onClick={() => handleStartEdit(list)}
                          className="edit-list-btn"
                          disabled={loading}
                          title="Edit List"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleDeleteList(list.id)}
                          className="delete-list-btn"
                          disabled={loading}
                          title="Delete List"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                    
                    {list.description && (
                      <p className="list-description">{list.description}</p>
                    )}
                    
                    <div className="list-meta">
                      <p className="list-created">
                        Created: {new Date(list.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <button
                      onClick={() => onSelectList(list.id)}
                      className="open-list-btn"
                      disabled={loading}
                    >
                      Open List →
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Statistics */}
      {userLists.length > 0 && (
        <div className="dashboard-stats">
          <p>You have {userLists.length} list{userLists.length !== 1 ? 's' : ''}</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;