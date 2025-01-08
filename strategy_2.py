import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime, requests
from alpaca_trade_api.rest import REST
from getpass import getpass
from get_news import NewsSentiment

class Backtest2():

    def __init__(self, ticker, start_date, end_date):

        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
    

    def generate_list_of_dates(self):
         # Convert start_date and end_date to datetime objects
        start_date_dt = datetime.datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end_date_dt = datetime.datetime.strptime(self.end_date, "%Y-%m-%d").date()

        # Generate all business days from start_date to end_date
        business_days = pd.date_range(start=start_date_dt, end=end_date_dt, freq='B')
        list_of_business_days = business_days.strftime('%Y-%m-%d').tolist()
        return list_of_business_days

    def test_strategy(self):

        analysis_df = pd.DataFrame()
        list_of_business_dates = self.generate_list_of_dates()
        stock = yf.download(self.ticker, start= self.start_date, end = self.end_date, interval="1d")
        stock.columns = stock.columns.to_flat_index()
        stock.reset_index(inplace=True)
        stock["Percent Change"] = stock[(f'Close', self.ticker)].pct_change().dropna()
        #stock["Sentiment"] = NewsSentiment(stock["Date"], ticker)
        for date_str in (list_of_business_dates):

            ## Generate market sentiment signal


            sentiment_analyser = NewsSentiment(date_str, self.ticker)
            sentiment = sentiment_analyser.return_news_sentiment()

            if sentiment == "Buy":
                stock.loc[stock["Date"] == date_str, "Strategy"] = 1
            elif sentiment == "Sell":
                stock.loc[stock["Date"] == date_str, "Strategy"] = -1
            elif sentiment == "Neutral":
                stock.loc[stock["Date"] == date_str, "Strategy"] = 0

            # Test Strategy

        stock['Strategy Return'] = stock['Strategy'].shift(1) * stock['Percent Change']
        stock['Strategy Return'].fillna(0, inplace=True)


        # Start with an initial capital of £5000

        initial_capital = 5000

        stock["Capital"] = (initial_capital * (1 + stock['Strategy Return']).cumprod())
        
        # Calculate capital over time

        end_of_day_capital = stock['Capital'].iloc[-1]
        total_return = (end_of_day_capital - initial_capital) / initial_capital

        analysis_df = pd.concat([analysis_df, stock], ignore_index=True)




            
        analysis_df.to_csv(f"AI_{self.ticker}_Data.csv", index=False)


        return analysis_df


if __name__ == "__main__":
    backtester = Backtest2("TSLA", "2024-12-01", "2024-12-30")
    news_strategy_df = backtester.test_strategy()    