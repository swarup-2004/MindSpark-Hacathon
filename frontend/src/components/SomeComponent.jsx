import React, { useState, useEffect } from 'react';
import axios from 'axios';
import api from '../services/api';

const SomeComponent = () => {
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');

    axios.get('http://127.0.0.1:8000/some-protected-api/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(response => {
      // Store the response data in localStorage
      localStorage.setItem('api_response', JSON.stringify(response.data));
    })
    .catch(error => {
      // Store the error message in state
      setError(error.message);
    });
  }, []);

  return (
    <div>
      {error && <p>Error: {error}</p>}
      <p>Data is stored in localStorage.</p>
    </div>
  );
};

export default SomeComponent;
