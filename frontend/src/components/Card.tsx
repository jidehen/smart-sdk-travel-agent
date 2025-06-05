import React from 'react';
import styled from 'styled-components';

interface CardProps {
    name: string;
    type: string;
    lastFour: string;
    imageSrc: string;
}

const CardContainer = styled.div`
    width: 300px; // Example width
    height: 180px; // Example height (standard card aspect ratio)
    background-color: #fff; // Default background, will be covered by image
    border-radius: 12px;
    margin: 10px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    background-size: cover;
    background-position: center;
    color: white; // Text color on the card
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5); // Add some text shadow for readability on busy backgrounds
`;

const CardName = styled.div`
    font-size: 1.2em;
    font-weight: bold;
`;

const CardDetails = styled.div`
    font-size: 0.9em;
`;

const Card: React.FC<CardProps> = ({ name, type, lastFour, imageSrc }) => {
    return (
        <CardContainer style={{ backgroundImage: `url(${imageSrc})` }}>
            <CardName>{name}</CardName>
            <CardDetails>
                <div>Type: {type}</div>
                <div>Last 4 Digits: {lastFour}</div>
            </CardDetails>
        </CardContainer>
    );
};

export default Card; 