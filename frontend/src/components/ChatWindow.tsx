import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import CardList from './CardList';

// Define the message interface
interface ChatMessage {
    text: string;
    isUser: boolean;
}

// Define the card data interface
interface CardData {
    card_id: string;
    type: string;
    brand: string;
    last4: string;
    nickname: string;
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
    // State for available cards
    const [availableCards, setAvailableCards] = useState<CardData[]>([]);
    // State for connection status
    const [isConnected, setIsConnected] = useState(false);
    // Reference to the WebSocket connection
    const wsRef = useRef<WebSocket | null>(null);
    // Reference to track if component is mounted
    const isMounted = useRef(true);
    // Reference to track connection attempts
    const connectionAttempts = useRef(0);

    // Function to connect to WebSocket
    const connectWebSocket = () => {
        if (!isMounted.current) {
            console.log('Component unmounted, skipping WebSocket connection');
            return;
        }

        connectionAttempts.current += 1;
        console.log(`Attempting WebSocket connection (attempt ${connectionAttempts.current})...`);

        try {
            // Create WebSocket connection
            const ws = new WebSocket('ws://localhost:5000');
            
            // Set up event handlers
            ws.onopen = () => {
                console.log('WebSocket connection established successfully');
                if (isMounted.current) {
                    setIsConnected(true);
                    connectionAttempts.current = 0;
                }
            };

            ws.onmessage = (event) => {
                console.log('Received message from server:', event.data);
                if (isMounted.current) {
                    try {
                        // Try to parse the message as JSON
                        const data = JSON.parse(event.data);
                        
                        // Check if this is a payment methods response
                        if (data.payment_methods && Array.isArray(data.payment_methods)) {
                            setAvailableCards(data.payment_methods);
                            // Add a message to indicate cards are displayed
                            setMessages(prev => [...prev, { 
                                text: "Here are your available payment methods:", 
                                isUser: false 
                            }]);
                        } else {
                            // Handle regular text messages
                            const contentRegex = /content='([^']+)'|content="([^"]+)"/g;
                            let match;
                            const contents = new Set<string>();

                            while ((match = contentRegex.exec(event.data)) !== null) {
                                contents.add(match[1] || match[2]);
                            }

                            if (contents.size > 0) {
                                contents.forEach((content) => {
                                    setMessages((prev) => {
                                        if (!prev.some((msg) => msg.text === content)) {
                                            return [...prev, { text: content, isUser: false }];
                                        }
                                        return prev;
                                    });
                                });
                            } else {
                                // Fallback: add the raw message if no content found
                                setMessages(prev => [...prev, { text: event.data, isUser: false }]);
                            }
                        }
                    } catch (error) {
                        console.error('Error processing message:', error);
                        // If JSON parsing fails, treat as regular text message
                        setMessages(prev => [...prev, { text: event.data, isUser: false }]);
                    }
                }
            };

            ws.onclose = (event) => {
                console.log(`WebSocket connection closed. Code: ${event.code}, Reason: ${event.reason}`);
                if (isMounted.current) {
                    setIsConnected(false);
                    if (connectionAttempts.current < 5) {
                        setTimeout(connectWebSocket, 5000);
                    } else {
                        console.error('Max connection attempts reached. Please check if the server is running.');
                    }
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error occurred:', error);
                if (isMounted.current) {
                    setIsConnected(false);
                }
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            if (isMounted.current && connectionAttempts.current < 5) {
                setTimeout(connectWebSocket, 5000);
            }
        }
    };

    // Connect to WebSocket when component mounts
    useEffect(() => {
        console.log('ChatWindow component mounted, initializing WebSocket connection...');
        isMounted.current = true;
        connectionAttempts.current = 0;
        connectWebSocket();

        return () => {
            console.log('ChatWindow component unmounting, cleaning up WebSocket connection...');
            isMounted.current = false;
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    // Function to handle sending messages
    const handleSendMessage = (message: string) => {
        console.log('Attempting to send message:', message);
        
        if (!isConnected) {
            console.error('Cannot send message - WebSocket is not connected');
            return;
        }

        // Add user's message to the chat
        setMessages(prev => [...prev, { text: message, isUser: true }]);
        // Clear available cards when user sends a new message
        setAvailableCards([]);

        // Send message through WebSocket
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            console.log('Sending message through WebSocket...');
            wsRef.current.send(message);
        } else {
            console.error('WebSocket is not in OPEN state. Current state:', wsRef.current?.readyState);
            connectWebSocket();
        }
    };

    return (
        <ChatContainer>
            <MessageList messages={messages} />
            <CardList cards={availableCards} />
            <MessageInput onSendMessage={handleSendMessage} />
        </ChatContainer>
    );
};

export default ChatWindow; 
