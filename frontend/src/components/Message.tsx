import React from 'react';
import styled from 'styled-components';

// Define the props interface for the Message component
interface MessageProps {
    // The text content of the message
    text: string;
    // Whether the message is from the user (true) or the assistant (false)
    isUser: boolean;
}

// Styled component for the message container
const MessageContainer = styled.div<{ isUser: boolean }>`
    // Add padding and margin to the message
    padding: 10px 15px;
    margin: 5px 0;
    // Round the corners
    border-radius: 15px;
    // Set maximum width to 70% of container
    max-width: 70%;
    // Align messages to the right if from user, left if from assistant
    align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
    // Set background color based on sender
    background-color: ${props => props.isUser ? '#007bff' : '#e9ecef'};
    // Set text color based on sender
    color: ${props => props.isUser ? 'white' : 'black'};
`;

// The Message component
const Message: React.FC<MessageProps> = ({ text, isUser }) => {
    return (
        <MessageContainer isUser={isUser}>
            {text}
        </MessageContainer>
    );
};

export default Message; 