import React, { useState } from 'react';
import { useAuth } from '../auth/AuthProvider';
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('https://5dd2cb6e-46b4-4091-876e-c53db58bf2c3-00-1ds1gj7x3v6j4.janeway.replit.dev:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password }),
      });

      if (response.ok) {
        const data = await response.json();
        login(data.role); // Store the role in context

        // Redirect to Home after successful login
        navigate('/');
      } else {
        alert('Invalid credentials');
      }
    } catch (error) {
      console.error('Error during login:', error);
      alert('Something went wrong. Please try again.');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        placeholder="name"
        value={identifier}
        onChange={(e) => setIdentifier(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Login</button>
    </form>
  );
};

export default LoginForm;
