// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/', // Your Django backend URL
});

// Optionally set up interceptors or other configurations here

export default api;
