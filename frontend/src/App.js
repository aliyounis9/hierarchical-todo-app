/**
 * Main Application Component
 * ========================
 * 
 * This is the root component that handles:
 * - Authentication state management
 * - Route protection and navigation
 * - Global app layout and structure
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams, useNavigate } from 'react-router-dom';
import './App.css';
import AuthForm from './components/AuthForm';
import Dashboard from './components/Dashboard';
import TaskList from './components/TaskList';
import { auth } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already authenticated on app load
  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      const response = await auth.checkAuth();
      
      if (response.authenticated && response.user) {
        setUser(response.user);
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setLoading(false);
  };

  const handleLogout = async () => {
    // Clear local authentication state immediately for responsive UX
    setUser(null);
    
    try {
      // Call logout API to clear server-side session
      await auth.logout();
    } catch (error) {
      // Silently handle API errors - user is already logged out locally
      // In production, this could be logged to an error tracking service
    }
  };

  // Component for protected routes
  // it checks if user is authenticated
  // if not, redirects to /login
  const ProtectedRoute = ({ children }) => {
    if (loading) return <div>Loading...</div>;
    return user ? children : <Navigate to="/login" replace />;
  };

  // Component for TaskList with URL params
  const TaskListPage = () => {
    const { listId } = useParams();
    const navigate = useNavigate();
    
    const handleBackToLists = () => {
      navigate('/dashboard');
    };

    return (
      <TaskList 
        selectedListId={listId}
        onBackToLists={handleBackToLists}
      />
    );
  };

  // Component for Dashboard with navigation
  const DashboardPage = () => {
    const navigate = useNavigate();
    
    const handleSelectList = (listId) => {
      navigate(`/list/${listId}`);
    };

    return (
      <Dashboard 
        user={user}
        onSelectList={handleSelectList}
        onLogout={handleLogout}
      />
    );
  };

  if (loading) {
    return (
      <div className="app-loading">
        <h2>Loading...</h2>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1> 📋 Hierarchical Todo App</h1>
      </header>
      
      <main className="App-main">
        <Router>
          <Routes>
            <Route 
              path="/login" 
              element={
                user ? <Navigate to="/dashboard" replace /> : 
                <AuthForm onAuthSuccess={handleAuthSuccess} isLogin={true} />
              } 
            />
            <Route 
              path="/register" 
              element={
                user ? <Navigate to="/dashboard" replace /> : 
                <AuthForm onAuthSuccess={handleAuthSuccess} isLogin={false} />
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/list/:listId" 
              element={
                <ProtectedRoute>
                  <TaskListPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/" 
              element={user ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />} 
            />
          </Routes>
        </Router>
      </main>
    </div>
  );
}

export default App;
