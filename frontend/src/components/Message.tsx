import React from 'react';
import styled from 'styled-components';

// Define the props interface for the Message component
interface MessageProps {
    text: string; // The text content of the message
    isUser: boolean; // Whether the message is from the user (true) or the assistant (false)
}

// Styled component for the message container
const MessageContainer = styled.div<{ isUser: boolean }>`
    padding: 10px 15px;
    margin: 5px 0;
    border-radius: 15px;
    max-width: 70%;
    align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
    background-color: ${props => props.isUser ? '#007bff' : '#e9ecef'};
    color: ${props => props.isUser ? 'white' : 'black'};
`;

const Message: React.FC<MessageProps> = ({ text, isUser }) => {
    // Convert Markdown-like syntax to HTML
    console.log("test " + text)
    const formattedText = text
        .replace(/\n/g, '<br>') // Convert newlines to <br>
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Convert **bold** to <strong>bold</strong>
    console.log("Formatted Text: " + formattedText);
    return (
        <MessageContainer isUser={isUser}>
            <div dangerouslySetInnerHTML={{ __html: formattedText }} />
        </MessageContainer>
    );
};

export default Message;
