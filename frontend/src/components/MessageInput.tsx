import React, { useState } from 'react';
import styled from 'styled-components';

// Define the props interface for MessageInput
interface MessageInputProps {
    // Function to call when a message is sent
    onSendMessage: (message: string) => void;
}

// Styled component for the input container
const InputContainer = styled.div`
    // Use flexbox for layout
    display: flex;
    // Add padding around the input
    padding: 20px;
    // Add a border at the top
    border-top: 1px solid #dee2e6;
    // Set background color
    background-color: white;
`;

// Styled component for the text input
const Input = styled.input`
    // Take up all available space
    flex: 1;
    // Add padding inside the input
    padding: 10px;
    // Add border
    border: 1px solid #dee2e6;
    // Round the corners
    border-radius: 4px;
    // Add margin to the right
    margin-right: 10px;
    // Set font size
    font-size: 16px;

    // Style for when input is focused
    &:focus {
        outline: none;
        border-color: #007bff;
    }
`;

// Styled component for the send button
const SendButton = styled.button`
    // Add padding
    padding: 10px 20px;
    // Set background color
    background-color: #007bff;
    // Set text color
    color: white;
    // Remove border
    border: none;
    // Round the corners
    border-radius: 4px;
    // Set cursor to pointer
    cursor: pointer;
    // Set font size
    font-size: 16px;

    // Style for when button is hovered
    &:hover {
        background-color: #0056b3;
    }

    // Style for when button is disabled
    &:disabled {
        background-color: #6c757d;
        cursor: not-allowed;
    }
`;

// The MessageInput component
const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage }) => {
    // State for the input value
    const [message, setMessage] = useState('');

    // Function to handle form submission
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (message.trim()) {
            onSendMessage(message);
            setMessage('');
        }
    };

    return (
        <InputContainer>
            <form onSubmit={handleSubmit} style={{ display: 'flex', width: '100%' }}>
                <Input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message..."
                />
                <SendButton type="submit" disabled={!message.trim()}>
                    Send
                </SendButton>
            </form>
        </InputContainer>
    );
};

export default MessageInput; 