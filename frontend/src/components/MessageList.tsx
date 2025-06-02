import React from 'react';
import styled from 'styled-components';
import Message from './Message';

// Define the message interface
interface ChatMessage {
    text: string;
    isUser: boolean;
}

// Define the props interface for MessageList
interface MessageListProps {
    // Array of messages to display
    messages: ChatMessage[];
}

// Styled component for the message list container
const MessageListContainer = styled.div`
    // Use flexbox for layout
    display: flex;
    flex-direction: column;
    // Add padding around the messages
    padding: 20px;
    // Allow scrolling when content overflows
    overflow-y: auto;
    // Set height to fill available space
    height: 100%;
    // Add some spacing between messages
    gap: 10px;
`;

// The MessageList component
const MessageList: React.FC<MessageListProps> = ({ messages }) => {
    return (
        <MessageListContainer>
            {messages.map((message, index) => (
                <Message
                    key={index}
                    text={message.text}
                    isUser={message.isUser}
                />
            ))}
        </MessageListContainer>
    );
};

export default MessageList; 