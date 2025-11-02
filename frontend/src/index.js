/**
 * React Application Entry Point
 * ============================
 * 
 * Initializes and renders the main App component.
 * Uses React 18's createRoot API for improved performance.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
