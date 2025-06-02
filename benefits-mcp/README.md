# Benefits MCP Server

A FastMCP server that provides card benefits, rewards rates, and multiplier information for Chase credit cards.

## Features

- Get rewards multipliers for different spending categories
- View card-specific benefits (lounge access, travel credits, etc.)
- Compare benefits across multiple cards
- Support for Chase card portfolio

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Available Cards

The server includes mock data for the following Chase cards:
- Chase Freedom
- Chase Freedom Unlimited
- Chase Sapphire Preferred
- Chase Sapphire Reserve

## API

### get_card_benefits

Get benefits information for one or more cards.

Request:
```python
{
    "card_ids": ["freedom", "sapphire_preferred"]
}
```

Response:
```python
{
    "cards": [
        {
            "card_id": "freedom",
            "card_name": "Chase Freedom",
            "annual_fee": 0.0,
            "multipliers": [
                {
                    "category": "rotating_categories",
                    "multiplier": 5.0,
                    "description": "5% cash back on up to $1,500 in combined purchases in rotating categories each quarter"
                },
                {
                    "category": "all_other_purchases",
                    "multiplier": 1.0,
                    "description": "1% cash back on all other purchases"
                }
            ],
            "perks": [
                {
                    "name": "No Annual Fee",
                    "description": "No annual fee",
                    "value": 0.0
                }
            ],
            "point_value": 1.0
        }
    ]
}
``` 