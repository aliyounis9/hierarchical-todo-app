/**
 * Task Component
 * =============
 * 
 * Individual task display and management:
 * - Hierarchical rendering with proper indentation
 * - Task editing, completion, and deletion
 * - Subtask creation and management
 * - Moving tasks between lists
 * - Urgency level visualization with colors
 */

import React, { useState } from 'react';
import { tasks, lists } from '../api';

const Task = ({ task, onTaskUpdate, onTaskDelete, level = 0, availableLists = [], onTaskMove }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description);
  const [editUrgency, setEditUrgency] = useState(task.urgency || 'medium');
  const [loading, setLoading] = useState(false);
  const [showAddSubtask, setShowAddSubtask] = useState(false);
  const [subtaskTitle, setSubtaskTitle] = useState('');
  const [subtaskDescription, setSubtaskDescription] = useState('');
  const [subtaskUrgency, setSubtaskUrgency] = useState('medium');
  const [subtaskError, setSubtaskError] = useState('');
  const [showMoveDropdown, setShowMoveDropdown] = useState(false);
  const [showCreateList, setShowCreateList] = useState(false);
  const [newListTitle, setNewListTitle] = useState('');

  const hasChildren = task.children && task.children.length > 0;
  const indentStyle = { marginLeft: `${level * 20}px` };

  // Urgency color mapping
  const urgencyColors = {
    low: '#28a745',      // Green
    medium: '#ffc107',   // Yellow  
    high: '#fd7e14',     // Orange
    urgent: '#dc3545'    // Red
  };

  const urgencyLabels = {
    low: '🟢',
    medium: '🟡', 
    high: '🟠',
    urgent: '🔴'
  };

  // Debug logging
  console.log('Task debug:', {
    taskId: task.id,
    level: level,
    availableListsCount: availableLists.length,
    shouldShowMoveButton: level === 0 && availableLists.length > 1
  });

  // Toggle task completion
  const handleToggleComplete = async () => {
    setLoading(true);
    try {
      await tasks.update(task.id, { completed: !task.completed });
      onTaskUpdate();
    } catch (error) {
      console.error('Failed to update task:', error);
    } finally {
      setLoading(false);
    }
  };

  // Save task edits
  const handleSaveEdit = async () => {
    setLoading(true);
    try {
      await tasks.update(task.id, {
        title: editTitle,
        description: editDescription,
        urgency: editUrgency,
      });
      setIsEditing(false);
      onTaskUpdate();
    } catch (error) {
      console.error('Failed to update task:', error);
    } finally {
      setLoading(false);
    }
  };

  // Cancel editing
  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setEditDescription(task.description);
    setEditUrgency(task.urgency || 'medium');
    setIsEditing(false);
  };

  // Delete task
  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task and all its subtasks?')) {
      setLoading(true);
      try {
        await tasks.delete(task.id);
        onTaskDelete();
      } catch (error) {
        console.error('Failed to delete task:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  // Add subtask
  const handleAddSubtask = async () => {
    if (!subtaskTitle.trim()) return;

    setLoading(true);
    setSubtaskError(''); // Clear any previous errors
    try {
      await tasks.createSubtask(task.id, {
        title: subtaskTitle,
        description: subtaskDescription,
        urgency: subtaskUrgency,
      });
      setSubtaskTitle('');
      setSubtaskDescription('');
      setSubtaskUrgency('medium');
      setShowAddSubtask(false);
      onTaskUpdate();
    } catch (error) {
      console.error('Failed to create subtask:', error);
      console.error('Error response:', error.response);
      
      // Check if it's a depth limit error
      const errorMessage = error.message || (error.response?.data?.error) || (error.response?.data?.message) || 'Unknown error';
      console.log('Error message from server:', errorMessage);
      
      if (errorMessage.includes('Maximum nesting depth reached') || errorMessage.includes('nesting depth')) {
        setSubtaskError('Cannot create more than 5 levels of nested tasks.');
      } else if (errorMessage.includes('depth')) {
        setSubtaskError('Cannot create more than 5 levels of nested tasks.');
      } else if (error.response?.data?.error) {
        setSubtaskError(error.response.data.error);
      } else {
        setSubtaskError('Failed to create subtask. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Move task to different list (only for top-level tasks)
  const handleMoveToList = async (newListId) => {
    if (level !== 0) return; // Only top-level tasks can be moved

    setLoading(true);
    try {
      await tasks.moveToList(task.id, newListId);
      setShowMoveDropdown(false);
      if (onTaskMove) {
        onTaskMove(); // Callback to refresh the current view
      }
    } catch (error) {
      console.error('Failed to move task:', error);
      alert('Failed to move task: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Create new list and move task to it
  const handleCreateNewListAndMove = async () => {
    if (!newListTitle.trim() || level !== 0) return;

    setLoading(true);
    try {
      // Create the new list (API expects name and description as separate params)
      const response = await lists.create(
        newListTitle,
        '' // Empty description
      );
      
      // Move the task to the new list
      await tasks.moveToList(task.id, response.list.id);
      
      // Reset state
      setNewListTitle('');
      setShowCreateList(false);
      setShowMoveDropdown(false);
      
      if (onTaskMove) {
        onTaskMove(); // Callback to refresh the current view
      }
    } catch (error) {
      console.error('Failed to create list and move task:', error);
      alert('Failed to create new list: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="task-container" style={indentStyle}>
      <div className={`task ${task.completed ? 'completed' : ''} depth-${task.depth}`}>
        <div className="task-header">
          {/* Collapse/Expand button */}
          {hasChildren && (
            <button
              className="collapse-btn"
              onClick={() => setIsCollapsed(!isCollapsed)}
              title={isCollapsed ? 'Expand' : 'Collapse'}
            >
              {isCollapsed ? '▶' : '▼'}
            </button>
          )}

          {/* Completion checkbox */}
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggleComplete}
            disabled={loading}
            className="task-checkbox"
          />

          {/* Task content */}
          <div className="task-content">
            {isEditing ? (
              <div className="task-edit">
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="edit-title"
                  disabled={loading}
                />
                <textarea
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  className="edit-description"
                  placeholder="Description..."
                  disabled={loading}
                />
                <select
                  value={editUrgency}
                  onChange={(e) => setEditUrgency(e.target.value)}
                  className="edit-urgency"
                  disabled={loading}
                >
                  <option value="low">🟢 Low Priority</option>
                  <option value="medium">🟡 Medium Priority</option>
                  <option value="high">🟠 High Priority</option>
                  <option value="urgent">🔴 Urgent</option>
                </select>
                <div className="edit-buttons">
                  <button onClick={handleSaveEdit} disabled={loading}>
                    Save
                  </button>
                  <button onClick={handleCancelEdit} disabled={loading}>
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="task-display">
                <div className="task-title-row">
                  <h4 className="task-title">{task.title}</h4>
                  <span 
                    className="urgency-indicator"
                    title={`Priority: ${task.urgency || 'medium'}`}
                  >
                    {urgencyLabels[task.urgency || 'medium']} {(task.urgency || 'medium').toUpperCase()}
                  </span>
                </div>
                {task.description && (
                  <p className="task-description">{task.description}</p>
                )}
                <div className="task-meta">
                  <span className="task-depth">Depth: {task.depth}</span>
                  <span className="task-id">ID: {task.id}</span>
                </div>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="task-actions">
            <button
              onClick={() => setIsEditing(!isEditing)}
              disabled={loading}
              className="edit-btn"
              data-tooltip={isEditing ? "Cancel Edit" : "Edit Task"}
            >
              ✏️
            </button>
            <button
              onClick={() => {
                setShowAddSubtask(!showAddSubtask);
                setSubtaskError(''); // Clear errors when toggling
              }}
              disabled={loading}
              className="add-subtask-btn"
              data-tooltip="Add Subtask"
            >
              ➕
            </button>
            {/* Move to List button - only for top-level tasks */}
            {level === 0 && (
              <button
                onClick={() => setShowMoveDropdown(!showMoveDropdown)}
                disabled={loading}
                className="move-btn"
                data-tooltip="Move to Different List"
              >
                🔄
              </button>
            )}
            <button
              onClick={handleDelete}
              disabled={loading}
              className="delete-btn"
              data-tooltip="Delete Task"
            >
              🗑️
            </button>
          </div>
        </div>

        {/* Add subtask form */}
        {showAddSubtask && (
          <div className="add-subtask-form">
            <h4>Add Subtask</h4>
            {subtaskError && (
              <div className="error-message">
                {subtaskError}
              </div>
            )}
            <input
              type="text"
              value={subtaskTitle}
              onChange={(e) => {
                setSubtaskTitle(e.target.value);
                setSubtaskError(''); // Clear error when user starts typing
              }}
              placeholder="Subtask title..."
              className="subtask-input"
              disabled={loading}
            />
            <textarea
              value={subtaskDescription}
              onChange={(e) => setSubtaskDescription(e.target.value)}
              placeholder="Subtask description (optional)..."
              className="subtask-description"
              disabled={loading}
              rows="2"
            />
            <select
              value={subtaskUrgency}
              onChange={(e) => setSubtaskUrgency(e.target.value)}
              className="subtask-urgency"
              disabled={loading}
            >
              <option value="low">🟢 Low Priority</option>
              <option value="medium">🟡 Medium Priority</option>
              <option value="high">🟠 High Priority</option>
              <option value="urgent">🔴 Urgent</option>
            </select>
            <div className="subtask-buttons">
              <button onClick={handleAddSubtask} disabled={loading || !subtaskTitle.trim()} className="add-btn">
                Add Subtask
              </button>
              <button onClick={() => setShowAddSubtask(false)} disabled={loading} className="cancel-btn">
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Move to list dropdown */}
        {showMoveDropdown && level === 0 && (
          <div className="move-list-form">
            <h4>Move task to:</h4>
            
            {/* Existing lists */}
            <div className="existing-lists">
              <h5>Existing Lists:</h5>
              {availableLists.length === 0 ? (
                <p><em>Loading lists...</em></p>
              ) : (
                <>
                  {availableLists
                    .filter(list => list.id !== task.list_id) // Don't show current list
                    .map(list => (
                      <button 
                        key={list.id}
                        onClick={() => handleMoveToList(list.id)}
                        disabled={loading}
                        className="list-option-btn"
                      >
                        📋 {list.title || list.name}
                      </button>
                    ))
                  }
                  {availableLists.filter(list => list.id !== task.list_id).length === 0 && (
                    <p><em>No other lists available</em></p>
                  )}
                </>
              )}
            </div>

            {/* Create new list option */}
            <div className="create-new-list">
              <h5>Or create new list:</h5>
              {!showCreateList ? (
                <button 
                  onClick={() => setShowCreateList(true)}
                  disabled={loading}
                  className="create-list-btn"
                >
                  ➕ Create New List
                </button>
              ) : (
                <div className="create-list-form">
                  <input
                    type="text"
                    value={newListTitle}
                    onChange={(e) => setNewListTitle(e.target.value)}
                    placeholder="New list name..."
                    disabled={loading}
                  />
                  <button 
                    onClick={handleCreateNewListAndMove}
                    disabled={loading || !newListTitle.trim()}
                  >
                    Create & Move
                  </button>
                  <button 
                    onClick={() => {
                      setShowCreateList(false);
                      setNewListTitle('');
                    }}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>

            {/* Close dropdown */}
            <button 
              onClick={() => {
                setShowMoveDropdown(false);
                setShowCreateList(false);
                setNewListTitle('');
              }} 
              disabled={loading}
              className="close-dropdown-btn"
            >
              ✕ Close
            </button>
          </div>
        )}
      </div>

      {/* Render children (subtasks) */}
      {hasChildren && !isCollapsed && (
        <div className="task-children">
          {task.children.map((child) => (
            <Task
              key={child.id}
              task={child}
              onTaskUpdate={onTaskUpdate}
              onTaskDelete={onTaskUpdate}
              level={level + 1}
              availableLists={availableLists}
              onTaskMove={onTaskMove}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Task;