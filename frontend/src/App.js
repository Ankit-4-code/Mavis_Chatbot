import React from 'react';
import './App.css';
import Chat from './Chat'; // Make sure this path is correct based on your project structure
import './style.css';
function App() {
  return (
    <div className="App">
      <div className="App-container">
        <div className="Title-container"> {/* Title container placed here for better alignment */}
          <span className="title">Mavis Chatbot</span>
        </div>
        <Chat />
      </div>
    </div>
  );
}

export default App; 