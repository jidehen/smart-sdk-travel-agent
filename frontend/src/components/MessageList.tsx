import React, { useEffect, useRef } from 'react';
import styled from 'styled-components';
import Message from './Message';

// Define the message interface
interface ChatMessage {
    text: string;
    isUser: boolean;
}

// Define the props interface for MessageList
interface MessageListProps {
    messages: ChatMessage[]; // Array of messages to display
}

// Styled component for the message list container
const MessageListContainer = styled.div`
    display: flex;
    flex-direction: column;
    padding: 20px;
    overflow-y: auto;
    height: 100%;
    gap: 10px;
`;

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
    const messageListRef = useRef<HTMLDivElement | null>(null);

    // Auto-scroll to the bottom of the message list when new messages are added
    useEffect(() => {
        if (messageListRef.current) {
            messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <MessageListContainer ref={messageListRef}>
            {messages.map((message, index) => (
                <Message key={index} text={message.text} isUser={message.isUser} />
            ))}
        </MessageListContainer>
    );
};

export default MessageList;
