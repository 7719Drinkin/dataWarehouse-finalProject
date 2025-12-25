import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Global styles
const globalStyles = `
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f0f2f5;
  }

  input, select, button {
    font-family: inherit;
  }

  input, select {
    width: 100%;
    padding: 8px 12px;
    margin-bottom: 8px;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    font-size: 14px;
  }

  input:focus, select:focus {
    outline: none;
    border-color: #1890ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  }

  label {
    display: block;
    margin-bottom: 4px;
    font-weight: 500;
    color: #333;
  }

  div > label + input,
  div > label + select {
    margin-top: 4px;
  }

  div > label + input + label,
  div > label + select + label {
    margin-top: 12px;
  }
`;

// Inject global styles
const styleSheet = document.createElement('style');
styleSheet.textContent = globalStyles;
document.head.appendChild(styleSheet);

const rootEl = document.getElementById('root');
if (!rootEl) {
  console.error('Root element with id="root" not found. Check public/index.html');
} else {
  const root = ReactDOM.createRoot(rootEl);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}