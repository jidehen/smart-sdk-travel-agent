import React from 'react';
import styled from 'styled-components';
import Card from './Card'; // Assuming Card.tsx is in the same directory

interface CardData {
    id?: string; // Optional ID if available or derived
    name: string;
    type: string;
    lastFour: string;
}

interface CardListProps {
    cards: CardData[];
}

const CardListContainer = styled.div`
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    padding: 20px;
    background-color: #e9ecef; // Light grey background for the wallet area
    border-radius: 8px;
    margin: 10px 0;
`;

// Helper function to get image path based on card name (example)
const getCardImageSrc = (cardName: string): string => {
    // For now, always use a fixed image file
    return `/images/cards/cardart.png`;
};


const CardList: React.FC<CardListProps> = ({ cards }) => {
    if (!cards || cards.length === 0) {
        return null; // Don't render if there are no cards
    }

    return (
        <CardListContainer>
            {cards.map((card) => (
                <Card
                    key={card.id || card.lastFour} // Use id or lastFour as key
                    name={card.name}
                    type={card.type}
                    lastFour={card.lastFour}
                    imageSrc={getCardImageSrc(card.name)} // Get image path (now fixed)
                />
            ))}
        </CardListContainer>
    );
};

export default CardList; 