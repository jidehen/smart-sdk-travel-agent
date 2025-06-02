import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

// Define the message interface
interface ChatMessage {
    text: string;
    isUser: boolean;
}

// Styled component for the chat window container
const ChatContainer = styled.div`
    // Set width and height
    width: 100%;
    height: 100vh;
    // Use flexbox for layout
    display: flex;
    flex-direction: column;
    // Set background color
    background-color: #f8f9fa;
`;

// The ChatWindow component
const ChatWindow: React.FC = () => {
    // State for messages
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    // Reference to the WebSocket connection
    const wsRef = useRef<WebSocket | null>(null);

    // Function to connect to WebSocket
    const connectWebSocket = () => {
        // Create WebSocket connection
        const ws = new WebSocket('ws://localhost:5000');
        
        // Set up event handlers
        ws.onopen = () => {
            console.log('Connected to WebSocket');
        };

        ws.onmessage = (event) => {
            // Add assistant's message to the chat
            setMessages(prev => [...prev, { text: event.data, isUser: false }]);
        };

        ws.onclose = () => {
            console.log('Disconnected from WebSocket');
            // Try to reconnect after 5 seconds
            setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        wsRef.current = ws;
    };

    // Connect to WebSocket when component mounts
    useEffect(() => {
        connectWebSocket();

        // Clean up WebSocket connection when component unmounts
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    // Function to handle sending messages
    const handleSendMessage = (message: string) => {
        // Add user's message to the chat
        setMessages(prev => [...prev, { text: message, isUser: true }]);

        // Send message through WebSocket
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(message);
        } else {
            console.error('WebSocket is not connected');
        }
    };

    return (
        <ChatContainer>
            <MessageList messages={messages} />
            <MessageInput onSendMessage={handleSendMessage} />
        </ChatContainer>
    );
};

export default ChatWindow; 