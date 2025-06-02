# SafePay Wallet MCP Server

A FastMCP server for managing user payment methods and account information.

## Overview

The SafePay Wallet MCP server provides functionality to:
- Retrieve user's available payment methods (credit cards, debit cards)
- Validate payment methods for transactions
- Handle different user profiles with varied card portfolios

## Features

- User-specific card portfolios
- Support for multiple card types (Freedom, Freedom Unlimited, Sapphire Preferred, Sapphire Reserve)
- Comprehensive validation checks (credit limit, daily limit, card status)
- Error handling for invalid user IDs or card IDs
- Detailed logging for debugging and monitoring

## MCP Tools

### get_payment_methods

Retrieves all payment methods for a specific user.

**Input:**
- `user_id`: String - The user's ID

**Output:**
List of payment methods with:
- `card_id`: String - Unique identifier for the card
- `type`: String - Card type (e.g., "credit")
- `brand`: String - Card brand (e.g., "Chase Freedom")
- `last4`: String - Last 4 digits of the card
- `nickname`: String - User-defined card nickname

### validate_payment_method

Validates if a payment method can handle a transaction.

**Input:**
- `user_id`: String - The user's ID
- `card_id`: String - The card's ID
- `amount`: Float - The transaction amount

**Output:**
Validation result with:
- `sufficient_credit`: Boolean - Whether the card has sufficient available credit
- `daily_limit_ok`: Boolean - Whether the transaction is within daily limit
- `card_active`: Boolean - Whether the card is active

## Mock Data

The server includes mock data for three user profiles with various Chase cards:
- User 1: Freedom and Sapphire Preferred
- User 2: Freedom Unlimited
- User 3: Sapphire Reserve and Freedom (inactive)

## Running the Server

1. Start the server:
```bash
python server/safepay_wallet_mcp_server.py
```

2. Run the test script:
```bash
python test_safepay_wallet_mcp.py
```

## Error Handling

The server handles various error cases:
- Invalid user IDs
- Invalid card IDs
- Insufficient credit
- Exceeded daily limits
- Inactive cards

All errors are logged with appropriate context for debugging.

## Logging

The server uses Python's logging module with the following configuration:
- Level: INFO
- Format: Timestamp, Logger Name, Level, File:Line, Message

## Dependencies

- FastMCP
- Pydantic
- Python 3.7+ 