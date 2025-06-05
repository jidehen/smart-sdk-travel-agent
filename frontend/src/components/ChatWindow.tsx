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
                    connectionAttempts.current = 0; // Reset attempts on successful connection
                }
            };

            // ws.onmessage = (event) => {
            //     console.log('Received message from server:', event.data);
            //     if (isMounted.current) {
            //         // Add assistant's message to the chat
            //         setMessages(prev => [...prev, { text: event.data, isUser: false }]);
            //     }
            // };

            ws.onmessage = (event) => {
                console.log('Received message from server:', event.data);
                if (isMounted.current) {
                    try {
                        // Regular expression to match content in different formats
                        const contentRegex = /content='([^']+)'|content="([^"]+)"/g;
                        let match;
                        const contents = new Set<string>(); // Use a Set to avoid duplicate messages

                        // Find all matches for content in the message
                        while ((match = contentRegex.exec(event.data)) !== null) {
                            // Add the matched content to the contents set
                            contents.add(match[1] || match[2]);
                        }

                        if (contents.size > 0) {
                            // Add each unique extracted content to the chat
                            contents.forEach((content) => {
                                // Check if the message is already in the chat to avoid duplicates
                                setMessages((prev) => {
                                    if (!prev.some((msg) => msg.text === content)) {
                                        return [...prev, { text: content as string, isUser: false }];
                                    }
                                    return prev;
                                });
                            });
                        } else {
                            console.error('No content found in message:', event.data);
                        }
                    } catch (error) {
                        console.error('Error processing message:', error);
                    }
                }
            };

            ws.onclose = (event) => {
                console.log(`WebSocket connection closed. Code: ${event.code}, Reason: ${event.reason}`);
                if (isMounted.current) {
                    setIsConnected(false);
                    // Try to reconnect after 5 seconds if we haven't exceeded max attempts
                    if (connectionAttempts.current < 5) {
                        console.log(`Scheduling reconnection attempt ${connectionAttempts.current + 1}...`);
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
                console.log(`Scheduling reconnection attempt ${connectionAttempts.current + 1}...`);
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

        // Clean up WebSocket connection when component unmounts
        return () => {
            console.log('ChatWindow component unmounting, cleaning up WebSocket connection...');
            isMounted.current = false;
            if (wsRef.current) {
                console.log('Closing existing WebSocket connection...');
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

        // Send message through WebSocket
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            console.log('Sending message through WebSocket...');
            wsRef.current.send(message);
        } else {
            console.error('WebSocket is not in OPEN state. Current state:', wsRef.current?.readyState);
            // Try to reconnect
            connectWebSocket();
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
