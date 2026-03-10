import axios from 'axios';

// Base URL is kept empty; Vite dev server will proxy API requests to the Flask backend
const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json'
  }
});

// This interceptor automatically adds token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    // must match case exactly with config.SECURITY_TOKEN_AUTHENTICATION_HEADER
    config.headers['Authentication-Token'] = token; 
  }
  return config;
});

export default api;