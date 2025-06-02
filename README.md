# SmartSDK Travel Agent

An intelligent travel assistant that helps users plan their travel and optimize their payment methods using multiple MCP servers.

## Features

- Flight search and booking assistance
- Payment method management and optimization
- Card benefits comparison and recommendations
- Integrated travel and payment planning

## Prerequisites

- Python 3.8+
- SmartSDK access
- Access to MCP servers:
  - Chase Travel MCP
  - Benefits MCP
  - SafePay Wallet MCP

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jidehen/smart-sdk-travel-agent.git
cd smart-sdk-travel-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the travel assistant:
```bash
python travel_assistant.py
```

Example queries:
- "Search for flights from New York to London"
- "What payment methods do I have available?"
- "Which card should I use for my flight purchase?"
- "Compare the benefits of my cards for travel purchases"

## Project Structure

```
smart-sdk-agent/
├── travel_assistant.py    # Main agent implementation
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Dependencies

- smart-sdk>=0.1.0
- requests>=2.31.0
- httpx<0.28.0

## License

This project is proprietary and confidential. 