import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import LoginScreen from './LoginScreen';
import App from './App';

const AppRouter = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authenticatedUser, setAuthenticatedUser] = useState(null);

  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    setAuthenticatedUser(userData);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setAuthenticatedUser(null);
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/" /> : <LoginScreen onLogin={handleLogin} />
        } />
        <Route path="/" element={
          isAuthenticated ? (
            <App 
              authenticatedUser={authenticatedUser} 
              handleLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" />
          )
        } />
      </Routes>
    </Router>
  );
};

export default AppRouter;

