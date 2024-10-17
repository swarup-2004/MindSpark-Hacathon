import React, { useState } from 'react';
import axios from 'axios'; // Import axios for making API requests
import '../App.css'; // Import CSS file for styling
import { useNavigate } from 'react-router-dom';

const LoginPopus = () => {
  const [username, setUsername] = useState(''); // Corrected to username
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const naviagate = useNavigate()
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post('http://127.0.0.1:8000/auth/jwt/create', {
        username: username, // Ensure username is sent
        password: password
      });
      
      // Save the JWT token in local storage or a cookie
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      // Redirect or update UI after successful login
      alert("Logged in successfully");
      // After successful login:
    const token = response.data.access; // Assuming 'access' is the key for JWT token
    localStorage.setItem('token', token);

      naviagate("/")
    } catch (err) {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="login-container">
      <div className="login-popup">
        <h2>Login</h2>
        <form onSubmit={handleSubmit}> {/* Corrected function name here */}
          <div className="input-group">
            <label>Username</label> {/* Changed email label to Username */}
            <input 
              type="text" 
              value={username}  // Corrected to username
              onChange={(e) => setUsername(e.target.value)}  // Updated handler
              placeholder="Enter your username" 
              required 
            />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Enter your password" 
              required 
            />
          </div>
          {error && <p className="error-text">{error}</p>} {/* Display error if exists */}
          <button type="submit" className="login-btn">Login</button>
        </form>
        <p className="signup-text">Don't have an account? <a href="/signup">Sign up here</a></p>
      </div>
    </div>
  );
};

export default LoginPopus;
