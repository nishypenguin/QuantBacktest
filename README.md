# Swing Strategy Backtester

A Python-based backtesting framework for testing swing-trading strategies on various tickers. This project leverages Yahoo Finance (`yfinance`) for historical data, computes technical indicators (e.g., **VWAP**, **RSI**, **ADX**), and optionally uses **news sentiment** to generate trading signals. Results are exported as CSV files.

---

## Table of Contents

1. [Features](#features)  
2. [Project Structure](#project-structure)  
3. [Installation & Setup](#installation--setup)  
4. [How to Use](#how-to-use)  
5. [Strategies Implemented](#strategies-implemented)  
6. [Customization](#customization)  
7. [License](#license)  

---

## Features

- **Technical Analysis**: Computes VWAP, RSI, ADX, etc.  
- **News Sentiment**: Integrates a custom `NewsSentiment` class to fetch sentiment signals.  
- **1-Minute & 1-Day Backtests**: Supports intraday (1-minute) and daily intervals.  
- **Portfolio Tracking**: Starts with an initial capital (e.g., $5,000) and calculates cumulative returns.  
- **CSV Outputs**: Stores backtest results in user-friendly CSV files for further analysis.

---

## Project Structure

```plaintext
.
├── swing_strategy.ipynb       # Jupyter notebook orchestrating all backtests
├── strategy.py                # Core Backtest class & strategy logic
├── get_news.py                # NewsSentiment class (not shown here but referenced)
├── 1_day_tesla_trend_momentum_strategy_backtest.csv
├── 1_day_tesla_inverse_trend_momentum_strategy_backtest.csv
├── 1_day_TSLA_news_strategy_backtest.csv
└── ... (other CSV outputs) ...
```
---

## Installation & Setup

Clone or Download this repository:
git clone https://github.com/yourusername/swing-strategy-backtester.git
cd swing-strategy-backtester
Install Dependencies (preferably in a virtual environment):
pip install -r requirements.txt
Make sure you have the following Python libraries installed:

pandas
numpy
yfinance
matplotlib
alpaca_trade_api
(Optional) Configure News API:
If the get_news.py file relies on API keys for sentiment analysis, make sure to:
Obtain the required API key(s).
Add them to an .env file or directly in the script.

---


## How to Use

Open the Jupyter Notebook:
jupyter notebook swing_strategy.ipynb
Edit the Parameters:
Set the tickers, start/end dates, and strategies to test in the notebook.
Run the Notebook:
Execute all cells in swing_strategy.ipynb to backtest the defined strategies.
CSV files will be generated for each backtested strategy.
Analyze the Results:
Open the generated CSV files to review strategy performance.
Analyze capital growth, returns, and signals for the given tickers.

---

## Strategies Implemented

1. Trend Momentum Strategy
This strategy uses VWAP, RSI, and ADX to identify trends and generate buy/sell signals.

Buy Condition:
Price > VWAP
RSI crossing above 30 (from below)
ADX > 25 (indicating a strong trend)
Sell Condition:
Price < VWAP
RSI crossing below 70 (from above)
ADX > 25

2. Inverse Trend Momentum Strategy
This strategy is similar to the trend momentum strategy but applies inverse logic, aiming to capture trend reversals.

Buy Condition:
Price < VWAP
RSI crossing above 70 (from below)
Sell Condition:
Price > VWAP
RSI crossing below 30 (from above)

3. News-Based Strategy
This strategy integrates market sentiment obtained via the NewsSentiment class. Sentiment values (Buy, Sell, or Neutral) guide trading decisions.

Buy: Enter a long position.
Sell: Enter a short position.
Neutral: No position is taken.

4. Intraday Strategy (1-Minute Bars)
Designed for short-term traders, this strategy operates on 1-minute bars. It combines VWAP, RSI, and news sentiment to make real-time decisions.

---

## Customization

Adjust Technical Indicators:
Modify RSI windows, ADX thresholds, VWAP configurations in strategy.py to test different parameter values, or AI prompts.


---

## Modify Risk Management

Update the starting capital or add position-sizing rules in the Backtest methods.
Add Stop Loss/Profit Targets and Intelligent Risk Management
Incorporate New Data:
Extend the code to fetch additional data, such as options data or fundamental metrics.

## Limitations

Use of OpenAI API requires a budget. We this being limited, I tested less data using sentiment analysis compared to the technical analysis

---

## Findings



---
