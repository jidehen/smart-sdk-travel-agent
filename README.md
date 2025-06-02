# SmartSDK Travel Agent

An intelligent travel assistant that helps users plan their travel and optimize their payment methods using multiple MCP servers.

## Features

- Flight search and booking assistance
- Payment method management and optimization
- Card benefits comparison and recommendations
- Integrated travel and payment planning

## Prerequisites

- Python 3.12
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

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
smart-sdk-travel-agent/
├── benefits-mcp/         # Benefits MCP server
├── chase-travel-mcp/     # Chase Travel MCP server
├── safepay-wallet-mcp/   # SafePay Wallet MCP server
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## Dependencies

- smart-sdk>=0.1.0
- requests>=2.31.0
- httpx<0.28.0

## License

This project is proprietary and confidential. 