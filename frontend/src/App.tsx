import React from 'react';
import styled from 'styled-components';
import ChatWindow from './components/ChatWindow';

// Styled component for the app container
const AppContainer = styled.div`
    // Set width and height
    width: 100%;
    height: 100vh;
    // Use flexbox for layout
    display: flex;
    flex-direction: column;
    // Set background color
    background-color: #ffffff;
`;

// The main App component
const App: React.FC = () => {
    return (
        <AppContainer>
            <ChatWindow />
        </AppContainer>
    );
};

export default App;
