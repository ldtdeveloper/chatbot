import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
const params = new URLSearchParams(window.location.search);
const token = params.get('token');

if (token) {
  localStorage.removeItem('token');
  localStorage.removeItem('user'); // If you also store user data
  
  localStorage.setItem('token', token);
  // clean URL immediately
  params.delete('token');
  const newUrl =
    window.location.pathname +
    (params.toString() ? `?${params}` : '');

  window.history.replaceState({}, '', newUrl);
}
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

