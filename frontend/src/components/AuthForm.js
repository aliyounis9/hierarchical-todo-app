/**
 * Authentication Form Component
 * ============================
 * 
 * Handles both user login and registration with:
 * - Form validation and error handling
 * - Loading states and user feedback
 * - Automatic navigation after successful auth
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../api';

const AuthForm = ({ onAuthSuccess, isLogin = true }) => {
  // isLogin is now a prop with default value of true
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let response;
      if (isLogin) {
        response = await auth.login(username, password);
        setSuccess('Login successful!');
      } else {
        response = await auth.register(username, email, password);
        setSuccess('Registration successful! You are now logged in.');
      }
      
      // Brief delay to show success message before navigation
      setTimeout(() => {
        onAuthSuccess(response.user);
      }, 1000);
      
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>{isLogin ? '🔑 Login to Your Account' : '🚀 Create New Account'}</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username:</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="email">Email:</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Loading...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>

        <p>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            className="link-button"
            onClick={() => navigate(isLogin ? '/register' : '/login')}
            disabled={loading}
          >
            {isLogin ? 'Register' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  );
};

export default AuthForm;