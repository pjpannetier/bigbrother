import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './LoginScreen.css'

const LoginScreen = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/api/users/login', { username, password });
      setMessage(response.data.message);
      onLogin({
        username: response.data.username,
        role: response.data.role,
        user_id: response.data.user_id
      });
      // Remove the navigation logic from here
    } catch (error) {
      setMessage(error.response?.data?.error || 'An error occurred');
    }
  };

  const handleRegister = () => {
    // Redirect to registration page
    console.log('Redirect to registration page');
  };

  const handleChangePassword = () => {
    // Redirect to change password page
    console.log('Redirect to change password page');
  };

  return (
    <div className="login-screen">
      <h2>Login to Big Brother</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
      <div className="additional-buttons">
        <button onClick={handleRegister}>Register</button>
        <button onClick={handleChangePassword}>Change Password</button>
      </div>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default LoginScreen;
