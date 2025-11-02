/**
 * TaskList Component
 * =================
 * 
 * Displays and manages tasks within a specific todo list:
 * - Show hierarchical task structure with indentation
 * - Create, edit, delete tasks and subtasks
 * - Move tasks between lists
 * - Bulk operations (complete all/uncheck all)
 */

import React, { useState, useEffect } from 'react';
import Task from './Task';
import { tasks, lists } from '../api';

const TaskList = ({ selectedListId, onBackToLists }) => {
  const [taskList, setTaskList] = useState(null);
  const [allTasks, setAllTasks] = useState([]);
  const [availableLists, setAvailableLists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAddTask, setShowAddTask] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskUrgency, setNewTaskUrgency] = useState('medium');

  // Load available lists for moving tasks between lists
  const loadAvailableLists = async () => {
    try {
      const response = await lists.getAll();
      setAvailableLists(response.lists || []);
    } catch (error) {
      // Set empty array on error to prevent UI issues
      setAvailableLists([]);
    }
  };

  // Load tasks for the selected list
  const loadTasks = async () => {
    if (!selectedListId) return;

    setLoading(true);
    setError('');
    
    try {
      // Get list details, tasks, and available lists
      const [listResponse, tasksResponse] = await Promise.all([
        lists.getById(selectedListId),
        tasks.getByList(selectedListId)
      ]);
      
      setTaskList(listResponse.list);
      setAllTasks(tasksResponse.tasks);
      
      // Also load available lists for moving
      await loadAvailableLists();
    } catch (error) {
      setError('Failed to load tasks: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Load tasks when component mounts or list changes
  useEffect(() => {
    loadTasks();
  }, [selectedListId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Add new top-level task
  const handleAddTask = async () => {
    if (!newTaskTitle.trim()) return;

    setLoading(true);
    try {
      await tasks.create({
        title: newTaskTitle,
        description: newTaskDescription,
        urgency: newTaskUrgency,
        list_id: selectedListId,
      });
      
      setNewTaskTitle('');
      setNewTaskDescription('');
      setNewTaskUrgency('medium');
      setShowAddTask(false);
      loadTasks(); // Refresh the task list
    } catch (error) {
      setError('Failed to create task: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle task move callback
  const handleTaskMove = () => {
    loadTasks(); // Refresh the current list after a task is moved
  };

  // Complete all tasks in the list
  const handleCompleteAll = async () => {
    if (!selectedListId) return;
    
    setLoading(true);
    try {
      await tasks.completeAll(selectedListId);
      loadTasks(); // Refresh to show updates
    } catch (error) {
      setError('Failed to complete all tasks: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Uncheck all tasks in the list  
  const handleUncheckAll = async () => {
    if (!selectedListId) return;
    
    setLoading(true);
    try {
      await tasks.uncheckAll(selectedListId);
      loadTasks(); // Refresh to show updates
    } catch (error) {
      setError('Failed to uncheck all tasks: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !taskList) {
    return <div className="loading">Loading tasks...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <p>{error}</p>
        <button onClick={loadTasks}>Retry</button>
      </div>
    );
  }

  if (!taskList) {
    return <div className="error">List not found</div>;
  }

  return (
    <div className="task-list-container">
      {/* Header */}
      <div className="task-list-header">
        <div className="header-top">
          <button onClick={onBackToLists} className="back-btn">
            ← Back to Lists
          </button>
          <div className="bulk-actions">
            <button 
              onClick={handleCompleteAll}
              disabled={loading || allTasks.length === 0}
              className="bulk-btn complete-all"
              title="Mark all tasks as complete"
            >
              ✅ Complete All
            </button>
            <button 
              onClick={handleUncheckAll}
              disabled={loading || allTasks.length === 0}
              className="bulk-btn uncheck-all"
              title="Mark all tasks as incomplete"
            >
              ❌ Uncheck All
            </button>
          </div>
        </div>
        <h2>{taskList.name}</h2>
        {taskList.description && (
          <p className="list-description">{taskList.description}</p>
        )}
      </div>

      {/* Add new task button */}
      <div className="add-task-section">
        {!showAddTask ? (
          <button 
            onClick={() => setShowAddTask(true)}
            className="add-task-btn"
            disabled={loading}
          >
            + Add New Task
          </button>
        ) : (
          <div className="add-task-form">
            <input
              type="text"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              placeholder="Task title..."
              className="task-title-input"
              disabled={loading}
            />
            <textarea
              value={newTaskDescription}
              onChange={(e) => setNewTaskDescription(e.target.value)}
              placeholder="Task description (optional)..."
              className="task-description-input"
              disabled={loading}
            />
            <select
              value={newTaskUrgency}
              onChange={(e) => setNewTaskUrgency(e.target.value)}
              className="task-urgency-input"
              disabled={loading}
            >
              <option value="low">🟢 Low Priority</option>
              <option value="medium">🟡 Medium Priority</option>
              <option value="high">🟠 High Priority</option>
              <option value="urgent">🔴 Urgent</option>
            </select>
            <div className="form-buttons">
              <button 
                onClick={handleAddTask}
                disabled={loading || !newTaskTitle.trim()}
              >
                Add Task
              </button>
              <button 
                onClick={() => {
                  setShowAddTask(false);
                  setNewTaskTitle('');
                  setNewTaskDescription('');
                  setNewTaskUrgency('medium');
                }}
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Tasks display */}
      <div className="tasks-container">
        {allTasks.length === 0 ? (
          <div className="no-tasks">
            <p>No tasks in this list yet.</p>
            <p>Click "Add New Task" to get started!</p>
          </div>
        ) : (
          <div className="tasks-list">
            {allTasks.map((task) => (
              <Task
                key={task.id}
                task={task}
                onTaskUpdate={loadTasks}
                onTaskDelete={loadTasks}
                level={0}
                availableLists={availableLists}
                onTaskMove={handleTaskMove}
              />
            ))}
          </div>
        )}
      </div>

      {/* Task statistics */}
      <div className="task-stats">
        <p>
          Total Tasks: {allTasks.length} | 
          Completed: {allTasks.filter(t => t.completed).length} | 
          Pending: {allTasks.filter(t => !t.completed).length}
        </p>
      </div>
    </div>
  );
};

export default TaskList;