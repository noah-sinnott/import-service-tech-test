import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Onboarding from './components/Onboarding/Onboarding';
import JobsList from './components/JobsList/JobsList';
import Dashboard from './components/Dashboard/Dashboard';
import { api, authUtils } from './api';

function AppContent() {
  const [isAuthenticated, setIsAuthenticated] = useState(authUtils.isAuthenticated());
  const location = useLocation();

  // Update auth state when location changes (after login/logout redirects)
  useEffect(() => {
    setIsAuthenticated(authUtils.isAuthenticated());
  }, [location]);

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
    window.location.href = '/login';
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🚀 Import Service</h1>
          {isAuthenticated && (
            <button className="btn-logout" onClick={handleLogout}>
              Logout
            </button>
          )}
        </div>
      </header>
      
      <div className="container">
        {isAuthenticated && (
          <nav className="nav">
            <NavLink
              to="/"
              className={({ isActive }) => isActive ? 'active' : ''}
              end
            >
              New Import
            </NavLink>
            <NavLink
              to="/jobs"
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              Jobs
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              Dashboard
            </NavLink>
          </nav>
        )}

        <Routes>
          <Route path="/login" element={
            isAuthenticated ? <Navigate to="/" replace /> : <Login />
          } />
          <Route path="/register" element={
            isAuthenticated ? <Navigate to="/" replace /> : <Register />
          } />
          <Route path="/" element={
            <ProtectedRoute>
              <Onboarding />
            </ProtectedRoute>
          } />
          <Route path="/jobs" element={
            <ProtectedRoute>
              <JobsList />
            </ProtectedRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
