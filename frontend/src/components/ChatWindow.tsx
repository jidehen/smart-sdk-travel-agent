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
    card_id: string; // card_id is required to match CardList.tsx
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
                    const messageText = event.data;

                    // Attempt to parse plain text card list format first
                    const cardListRegex = /\d+\. (.*?)\n - Type: (.*?)\n - Last 4 Digits: (.*?)\n - Nickname: (.*?)(?:\n|$)/g;
                    let match;
                    const parsedCards: CardData[] = [];
                    let index = 0; // Use index to generate a simple unique id for plain text cards

                    // Find all card entries in the text message
                    while ((match = cardListRegex.exec(messageText)) !== null) {
                        const brand = match[1].trim();
                        const type = match[2].trim();
                        const last4 = match[3].trim();
                        const nickname = match[4].trim();
                        
                        parsedCards.push({
                            card_id: `temp-${index}`, // Generate a temporary id
                            brand,
                            type,
                            last4,
                            nickname,
                        });
                        index++;
                    }

                    if (parsedCards.length > 0) {
                        // If plain text card list found and parsed successfully
                        setAvailableCards(parsedCards);
                        // Add a simple text message indicating cards are displayed
                        setMessages(prev => [...prev, { 
                            text: "Here are your available payment methods:", 
                            isUser: false 
                        }]);
                    } else {
                        // If not the plain text card list, try processing as regular message/JSON (fallback)
                        try {
                            const data = JSON.parse(messageText);
                            
                            // Check if this is a structured payment methods response (future compatibility)
                            if (data.payment_methods && Array.isArray(data.payment_methods)) {
                                // Map the mock data structure to the CardData interface
                                const structuredCards: CardData[] = data.payment_methods.map((card: any) => ({
                                    card_id: card.card_id,
                                    brand: card.brand,
                                    type: card.type,
                                    last4: card.last4,
                                    nickname: card.nickname,
                                }));
                                setAvailableCards(structuredCards);
                                setMessages(prev => [...prev, { 
                                    text: "Here are your available payment methods:", 
                                    isUser: false 
                                }]);
                            } else {
                                 // If not a recognized structured format, add as a regular text message
                                const contentRegex = /content='([^']+)'|content="([^"]+)"/g;
                                let contentMatch;
                                const contents = new Set<string>();

                                while ((contentMatch = contentRegex.exec(messageText)) !== null) {
                                    contents.add(contentMatch[1] || contentMatch[2]);
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
                                    setMessages(prev => [...prev, { text: messageText, isUser: false }]);
                                }
                            }
                        } catch (error) {
                            // If JSON parsing fails, and not the plain text card list, treat as plain text
                             console.error('Error parsing message as JSON or other structured format:', error);
                            setMessages(prev => [...prev, { text: messageText, isUser: false }]);
                        }
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
            {/* Render the CardList component if availableCards is not empty */}
            {availableCards.length > 0 ? <CardList cards={availableCards} /> : null}
            <MessageInput onSendMessage={handleSendMessage} />
        </ChatContainer>
    );
};

export default ChatWindow; 
