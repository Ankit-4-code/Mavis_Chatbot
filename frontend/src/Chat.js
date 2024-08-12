import React, { useState} from 'react';
import { sendMessage } from './api';
import { FaMicrophone, FaStop } from 'react-icons/fa'; 
function Chat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    
    // Utility function to ensure the API response is valid and properly formatted
    const getContent = (response) => {
        // Ensure response and nested properties exist
        if (response && response.message) {
            return response.message.message;  
        } else {
            console.log('Invalid or no response:', JSON.stringify(response)); // Log the actual response for deeper inspection
            return 'No valid response received';
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMessage = { role: 'user', content: input };
        setMessages(messages => [...messages, userMessage]);
    
        try {
            const response = await sendMessage(input);
            console.log('Received response:', response);  // Log the raw response for debugging
            const botMessage = {
                role: 'bot',
                content: getContent(response)  
            };
            // Update messages state to include the bot's response and log the updated state
        setMessages(messages => {
            const updatedMessages = [...messages, botMessage];
            console.log('Updated messages:', updatedMessages);  // Log the updated messages array
            return updatedMessages;
        });
        } catch (error) {
            console.error('Handle Send Error:', error);
            setMessages(messages => [...messages, { role: 'bot', content: 'Error communicating with the backend 1.' }]);
        }
    
        setInput('');
    };

    const handleKeyPress = (event) => {
        console.log('handleSend called');
        if (event.key === 'Enter') {
            handleSend();
        }
    };

    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
            </div>
            <div className="chat-input-container">
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type a message..."
                />
                <button onClick={handleSend}>
                    <i className="fas fa-arrow-right"></i> {/* Font Awesome icon */}
                </button>
            </div>
        </div>
    );
}

export default Chat;