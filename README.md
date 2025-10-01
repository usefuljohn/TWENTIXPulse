# PoolPulse

A simple BitShares Liquidity Pool Exchange Rate Calculator with a graphical user interface.

## Description

PoolPulse is a Python application that fetches liquidity pool data from the BitShares blockchain, calculates exchange rates between assets, and displays the distribution of TWENTIX in various liquidity pools as a pie chart.

## Features

- Fetches liquidity pool data from multiple BitShares API endpoints.
- Calculates exchange rates with proper precision.
- Displays a pie chart of TWENTIX pool contributions.
- Shows the total TWENTIX amount, TWENTIX/USD price, and Total Value Locked (TVL).

## Requirements

- Python 3
- tkinter
- matplotlib
- numpy
- requests

## Installation

1. Clone the repository.
2. Install the required packages:

```bash
/venv/bin/pip install matplotlib numpy requests
```

## Usage

To run the application, execute the following command:

```bash
./run.sh
```
