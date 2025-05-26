import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { Web3ContextProvider } from './contexts/Web3Context'
import { NotificationProvider } from './contexts/NotificationContext'

console.log('main.jsx executing'); // Debug log

// Ensure root element exists
const rootElement = document.getElementById('root')
if (!rootElement) {
  const root = document.createElement('div')
  root.id = 'root'
  document.body.appendChild(root)
}

// Create root and render app
const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
  <React.StrictMode>
    <NotificationProvider>
      <Web3ContextProvider>
        <App />
      </Web3ContextProvider>
    </NotificationProvider>
  </React.StrictMode>
)