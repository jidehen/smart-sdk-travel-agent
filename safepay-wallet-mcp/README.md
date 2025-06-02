# SafePay Wallet MCP Server

A FastMCP server for managing user payment methods and account information.

## Overview

The SafePay Wallet MCP server provides functionality to:
- Retrieve user's available payment methods (credit cards, debit cards)
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

## Mock Data

The server includes mock data for three user profiles with various Chase cards:
- User 1: Freedom and Sapphire Preferred
- User 2: Freedom Unlimited
- User 3: Sapphire Reserve and Freedom (inactive)

## Dependencies

- FastMCP
- Pydantic
- Python 3.12+ 