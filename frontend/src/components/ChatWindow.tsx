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
                    let isCardMessage = false; // Flag to indicate if the message is a card list

                    // Attempt to parse the specific plain text card list format first
                    // This regex captures the full structure including intro and outro
                    const fullCardListRegex = /User\d+ has the following available cards:\n\n((?:\d+\. .*?\n - Type: .*?\n - Last 4 Digits: .*?\n - Nickname: .*?\n\n)+)if\nyou need more information about these cards or assistance with anything else, just let me know!/s;
                    const fullMatch = messageText.match(fullCardListRegex);

                    if (fullMatch && fullMatch[1]) {
                        // If the full card list structure is matched
                        isCardMessage = true;
                        const cardEntriesText = fullMatch[1];
                        const cardEntryRegex = /\d+\. (.*?)\n - Type: (.*?)\n - Last 4 Digits: (.*?)\n - Nickname: (.*?)(?:\n|$)/g;
                        let cardMatch;
                        const parsedCards: CardData[] = [];
                        let index = 0;

                        // Reset lastIndex before executing the regex in a loop
                        cardEntryRegex.lastIndex = 0;
                        while ((cardMatch = cardEntryRegex.exec(cardEntriesText)) !== null) {
                            const brand = cardMatch[1].trim();
                            const type = cardMatch[2].trim();
                            const last4 = cardMatch[3].trim();
                            const nickname = cardMatch[4].trim();
                            
                            parsedCards.push({
                                card_id: `temp-${index}`,
                                brand,
                                type,
                                last4,
                                nickname,
                            });
                            index++;
                        }
                        setAvailableCards(parsedCards);
                    } else {
                        // If not the plain text card list, try parsing as JSON (future compatibility)
                        try {
                            const data = JSON.parse(messageText);
                            
                            // Check if this is a structured payment methods response
                            if (data.payment_methods && Array.isArray(data.payment_methods)) {
                                 // The mock data structure already matches CardData
                                setAvailableCards(data.payment_methods);
                                isCardMessage = true; // Mark as a card message
                            }
                        } catch (error) {
                             // JSON parsing failed, not a JSON message
                             console.log('Message is not JSON, trying other formats...', error);
                        }
                    }

                    // If the message was not a card list, add it as a regular text message
                    if (!isCardMessage) {
                         const contentRegex = /content='([^']+)'|content="([^"]+)"/g;
                         let contentMatch;
                         const contents = new Set<string>();

                        // Reset lastIndex before executing the regex in a loop
                        contentRegex.lastIndex = 0;
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
                             // Fallback: add the raw message if no recognized format
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
            {/* Render the CardList component if availableCards is not empty, otherwise render messages */}
            {availableCards.length > 0 ? (
                <CardList cards={availableCards} />
            ) : (
                <MessageList messages={messages} />
            )}
            <MessageInput onSendMessage={handleSendMessage} />
        </ChatContainer>
    );
};

export default ChatWindow; 
