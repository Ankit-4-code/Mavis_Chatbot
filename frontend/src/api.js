import axios from 'axios';

const API_URL = 'http://localhost:9000/api'; // Match the backend port

export const sendMessage = async (message, conversationId) => {
    try {
        const response = await axios.post(API_URL, {
            message: message,
            conversation_id: conversationId
        
        });
        console.log("API Response:", response.data); 
        return response.data;
    } catch (error) {
        console.error('Error sending message:', error.response ? error.response.data : error);
        return { message: 'Error communicating with the backend.' };
    }
};

export const sendAudio = async (audioBlob, conversationId) => {
    try {
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.wav');
        formData.append('conversation_id', conversationId);

        const response = await axios.post(API_URL, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        console.log("Audio API Response:", response.data);
        return response.data;
    } catch (error) {
        console.error('Error sending audio:', error.response ? error.response.data : error);
        return { message: 'Error communicating with the backend.' };
    }
};