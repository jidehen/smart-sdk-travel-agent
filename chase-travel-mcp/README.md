# Chase Travel MCP Server

MCP server for searching and retrieving flight information.

## Overview

This MCP server provides flight search capabilities with the following features:
- Search flights based on origin, destination, dates, and passenger count
- Support for multiple airports per city (e.g., NYC = JFK, LGA, EWR)
- Detailed flight information including times, airlines, aircraft, and stops
- Consistent pricing and availability data

## Prerequisites

- Python 3.12
- FastMCP package

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Available Tools

#### search_flights

Search for flights based on specified criteria.

Input parameters:
- `origin`: Origin city code (e.g., "NYC", "LA")
- `destination`: Destination city code
- `departure_date`: Departure date
- `return_date`: Return date (optional)
- `passengers`: Number of passengers (default: 1)
- `class_type`: Class type (default: "economy")

Output:
- List of flights with details including:
  - Flight ID
  - Airline
  - Origin/Destination
  - Departure/Arrival times
  - Duration
  - Number of stops
  - Price
  - Class type

## Mock Data

The server includes mock flight data for popular US routes:
- NYC-MIA
- LAX-LAS
- Various airlines (American, Delta, United, Southwest, JetBlue)
- Realistic pricing ranges ($200-800 for domestic flights)
- Mix of nonstop and 1-stop flights

## City to Airport Mappings

The server supports multiple airports per city:
- NYC: JFK, LGA, EWR
- LA: LAX, BUR, ONT
- Chicago: ORD, MDW
- Miami: MIA, FLL
- Las Vegas: LAS 