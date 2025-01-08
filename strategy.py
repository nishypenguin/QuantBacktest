import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime, requests
from alpaca_trade_api.rest import REST
from getpass import getpass
from get_news import NewsSentiment

class Backtest():

    def __init__(self, ticker, start_date, period, end_date):

        self.ticker = ticker
        self.start_date = start_date
        self.period = period
        self.end_date = end_date
    

    def generate_list_of_dates(self):
        start_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d").date()
        business_days = pd.date_range(start=start_date, periods=self.period, freq='B')
        list_of_business_days = business_days.strftime('%Y-%m-%d').tolist()
        return list_of_business_days

    def test_strategy_1_min(self):

        analysis_df = pd.DataFrame()
        
        list_of_business_dates = self.generate_list_of_dates()
        ticker = self.ticker
        for index in range(len(list_of_business_dates)-1):
            stock = yf.download(self.ticker, start= list_of_business_dates[index], end=list_of_business_dates[index + 1], interval="1m")
            stock.columns = stock.columns.to_flat_index()

            ## Generate VWAP and RSI

            stock["Reference Price"] = (stock[(f'High', ticker)] + stock[(f'Low', ticker)] + stock[(f'Close', ticker)]) / 3
            stock["Reference Price * Volume"] = stock["Reference Price"] * stock[(f'Volume', ticker)]
            stock["(Reference Price * Volume) Sum"] = stock["Reference Price * Volume"].cumsum()
            stock["Volume Sum"] = stock[(f'Volume', ticker)].cumsum()
            stock["VWAP"] = stock["(Reference Price * Volume) Sum"] / stock["Volume Sum"]

            stock["Price Difference"] = stock[(f'Close', ticker)].diff()
            stock["Gain"] = np.where(stock["Price Difference"] > 0, stock["Price Difference"], 0)
            stock["Loss"] = np.where(stock["Price Difference"] < 0, -stock["Price Difference"], 0)
            stock['Avg Gain'] = stock['Gain'].rolling(window=10, min_periods=1).mean()
            stock['Avg Loss'] = stock['Loss'].rolling(window=10, min_periods=1).mean()
            stock["RS"] = stock['Avg Gain'].div(stock['Avg Loss'])
            stock["RSI"] = 100 - (100 /(1 + stock["RS"]))

            ## Add Additional Columns for Analysis

            stock["Percent Change"] = stock[(f'Close', ticker)].pct_change().dropna()

            ## Generate market sentiment signal

            start_date = list_of_business_dates[index]
            sentiment_analyser = NewsSentiment(start_date)
            sentiment = sentiment_analyser.return_news_sentiment()

            stock = stock.reset_index()

            stock["Sentiment"] = sentiment

            if sentiment == "Buy":

                # Define strategy 

                stock["Strategy"] = 0

                # Condition 1: VWAP is increasing and Close > VWAP and RSI < increasing from under 30 to over 30
                stock.loc[
                    (stock["VWAP"] > stock["VWAP"].shift()) & (stock["VWAP"] < stock[("Close", ticker)]) & (stock["RSI"].shift() < 30) & (stock["RSI"] > 30),
                    "Strategy",
                ] = 1

            elif sentiment == "Sell":

                # Define strategy 

                stock["Strategy"] = 0

                # Condition : VWAP is decreasing and Close < VWAP and RSI decreasing from 70 to below 70 
                stock.loc[
                    (stock["VWAP"] < stock["VWAP"].shift()) & (stock["VWAP"] > stock[("Close", ticker)]) & (stock["RSI"].shift() > 70) & (stock["RSI"] < 70),
                    "Strategy",
                ] = -1

            elif sentiment == "Neutral":

                # Define strategy

                stock["Strategy"] = 0

                # Test Strategy

            stock['Strategy Return'] = stock['Strategy'].shift(1) * stock['Percent Change']
            stock['Strategy Return'].fillna(0, inplace=True)


            # Start with an initial capital of £5000

            initial_capital = 5000

            stock["Capital"] = (initial_capital * (1 + stock['Strategy Return']).cumprod())
            
            # Calculate capital over time

            #end_of_day_capital = stock['Capital'].iloc[-1]
            #total_return (end_of_day_capital - initial_capital) / initial_capital


            analysis_df = pd.concat([analysis_df, stock], ignore_index=True)




            
        

        return analysis_df
    
    def test_1_day_trend_momentum_strategy(self):

        analysis_df = pd.DataFrame()
        ticker = self.ticker
        stock = yf.download(self.ticker, start= self.start_date, end = self.end_date, interval="1d")
        stock.columns = stock.columns.to_flat_index()

        ## Generate VWAP,RSI and ADX

        stock["Reference Price"] = (stock[(f'High', ticker)] + stock[(f'Low', ticker)] + stock[(f'Close', ticker)]) / 3
        stock["Reference Price * Volume"] = stock["Reference Price"] * stock[(f'Volume', ticker)]
        stock["(Reference Price * Volume) Sum"] = stock["Reference Price * Volume"].cumsum()
        stock["Volume Sum"] = stock[(f'Volume', ticker)].cumsum()
        stock["VWAP"] = stock["(Reference Price * Volume) Sum"] / stock["Volume Sum"]

        stock["Price Difference"] = stock[(f'Close', ticker)].diff()
        stock["Gain"] = np.where(stock["Price Difference"] > 0, stock["Price Difference"], 0)
        stock["Loss"] = np.where(stock["Price Difference"] < 0, -stock["Price Difference"], 0)
        stock['Avg Gain'] = stock['Gain'].rolling(window=10, min_periods=1).mean()
        stock['Avg Loss'] = stock['Loss'].rolling(window=10, min_periods=1).mean()
        stock["RS"] = stock['Avg Gain'].div(stock['Avg Loss'])
        stock["RSI"] = 100 - (100 /(1 + stock["RS"]))
         
        # Calclulate ADX

                    # True Range (TR)
        stock["High-Low"] = stock[(f'High', ticker)] - stock[(f'Low', ticker)]
        stock["High-PrevClose"] = np.abs(stock[(f'High', ticker)] - stock[(f'Close', ticker)].shift())
        stock["Low-PrevClose"] = np.abs(stock[(f'Low', ticker)] - stock[(f'Close', ticker)].shift())
        stock["TR"] = stock[["High-Low", "High-PrevClose", "Low-PrevClose"]].max(axis=1)

        # Directional Movement (DM)
        stock["+DM"] = np.where(
            (stock[(f'High', ticker)].diff() > stock[(f'Low', ticker)].diff()) & 
            (stock[(f'High', ticker)].diff() > 0), 
            stock[(f'High', ticker)].diff(), 
            0
        )
        stock["-DM"] = np.where(
            (stock[(f'Low', ticker)].diff() > stock[(f'High', ticker)].diff()) & 
            (stock[(f'Low', ticker)].diff() > 0), 
            -stock[(f'Low', ticker)].diff(), 
            0
        )

        # Smooth +DM, -DM, and TR using rolling average (similar to ATR calculation)
        period = 14  # Default period for ADX
        stock["Smoothed TR"] = stock["TR"].rolling(window=period).mean()
        stock["Smoothed +DM"] = stock["+DM"].rolling(window=period).mean()
        stock["Smoothed -DM"] = stock["-DM"].rolling(window=period).mean()

        # Calculate +DI, -DI
        stock["+DI"] = (stock["Smoothed +DM"] / stock["Smoothed TR"]) * 100
        stock["-DI"] = (stock["Smoothed -DM"] / stock["Smoothed TR"]) * 100

        # Calculate DX
        stock["DX"] = (np.abs(stock["+DI"] - stock["-DI"]) / (stock["+DI"] + stock["-DI"])) * 100

    
        stock["ADX"] = stock["DX"].rolling(window=period).mean()

        # Clean up intermediary columns if necessary
        stock = stock.drop(columns=["High-Low", "High-PrevClose", "Low-PrevClose"])

        ## Add Additional Columns for Analysis

        stock["Percent Change"] = stock[(f'Close', ticker)].pct_change().dropna()

            # Define strategy 

        stock["Strategy"] = 0

        # Condition 1: Close > VWAP and RSI < increasing from under 30 to over 30 and ADX > 25
        stock.loc[
            (stock["VWAP"] < stock[("Close", ticker)]) & (stock["RSI"].shift() < 30) & (stock["RSI"] > 30) & (stock["ADX"] > 25),
            "Strategy",
        ] = 1

        # Condition 2: VWAP is decreasing and Close < VWAP and RSI decreasing from 70 to below 70 
        stock.loc[
            (stock["VWAP"] > stock[("Close", ticker)]) & (stock["RSI"].shift() > 70) & (stock["RSI"] < 70) & (stock["ADX"] > 25),
            "Strategy",
        ] = -1

           

        stock['Strategy Return'] = stock['Strategy'].shift(1) * stock['Percent Change']
        stock['Strategy Return'].fillna(0, inplace=True)

    

        # Start with an initial capital of £5000

        initial_capital = 5000

        stock["Capital"] = (initial_capital * (1 + stock['Strategy Return']).cumprod())
        
        # Calculate capital over time

        #end_of_day_capital = stock['Capital'].iloc[-1]
        #total_return (end_of_day_capital - initial_capital) / initial_capital


        analysis_df = pd.concat([analysis_df, stock], ignore_index=True)



        return analysis_df
    
    def test_1_day_inverse_trend_momentum_strategy(self):

        analysis_df = pd.DataFrame()
        ticker = self.ticker
        stock = yf.download(self.ticker, start= self.start_date, end = self.end_date, interval="1d")
        stock.columns = stock.columns.to_flat_index()

        ## Generate VWAP,RSI and ADX

        stock["Reference Price"] = (stock[(f'High', ticker)] + stock[(f'Low', ticker)] + stock[(f'Close', ticker)]) / 3
        stock["Reference Price * Volume"] = stock["Reference Price"] * stock[(f'Volume', ticker)]
        stock["(Reference Price * Volume) Sum"] = stock["Reference Price * Volume"].cumsum()
        stock["Volume Sum"] = stock[(f'Volume', ticker)].cumsum()
        stock["VWAP"] = stock["(Reference Price * Volume) Sum"] / stock["Volume Sum"]

        stock["Price Difference"] = stock[(f'Close', ticker)].diff()
        stock["Gain"] = np.where(stock["Price Difference"] > 0, stock["Price Difference"], 0)
        stock["Loss"] = np.where(stock["Price Difference"] < 0, -stock["Price Difference"], 0)
        stock['Avg Gain'] = stock['Gain'].rolling(window=10, min_periods=1).mean()
        stock['Avg Loss'] = stock['Loss'].rolling(window=10, min_periods=1).mean()
        stock["RS"] = stock['Avg Gain'].div(stock['Avg Loss'])
        stock["RSI"] = 100 - (100 /(1 + stock["RS"]))
         
        # Calclulate ADX

                    # True Range (TR)
        stock["High-Low"] = stock[(f'High', ticker)] - stock[(f'Low', ticker)]
        stock["High-PrevClose"] = np.abs(stock[(f'High', ticker)] - stock[(f'Close', ticker)].shift())
        stock["Low-PrevClose"] = np.abs(stock[(f'Low', ticker)] - stock[(f'Close', ticker)].shift())
        stock["TR"] = stock[["High-Low", "High-PrevClose", "Low-PrevClose"]].max(axis=1)

        # Directional Movement (DM)
        stock["+DM"] = np.where(
            (stock[(f'High', ticker)].diff() > stock[(f'Low', ticker)].diff()) & 
            (stock[(f'High', ticker)].diff() > 0), 
            stock[(f'High', ticker)].diff(), 
            0
        )
        stock["-DM"] = np.where(
            (stock[(f'Low', ticker)].diff() > stock[(f'High', ticker)].diff()) & 
            (stock[(f'Low', ticker)].diff() > 0), 
            -stock[(f'Low', ticker)].diff(), 
            0
        )

        # Smooth +DM, -DM, and TR using rolling average (similar to ATR calculation)
        period = 14  # Default period for ADX
        stock["Smoothed TR"] = stock["TR"].rolling(window=period).mean()
        stock["Smoothed +DM"] = stock["+DM"].rolling(window=period).mean()
        stock["Smoothed -DM"] = stock["-DM"].rolling(window=period).mean()

        # Calculate +DI, -DI
        stock["+DI"] = (stock["Smoothed +DM"] / stock["Smoothed TR"]) * 100
        stock["-DI"] = (stock["Smoothed -DM"] / stock["Smoothed TR"]) * 100

        # Calculate DX
        stock["DX"] = (np.abs(stock["+DI"] - stock["-DI"]) / (stock["+DI"] + stock["-DI"])) * 100

    
        stock["ADX"] = stock["DX"].rolling(window=period).mean()

        # Clean up intermediary columns if necessary
        stock = stock.drop(columns=["High-Low", "High-PrevClose", "Low-PrevClose"])

        ## Add Additional Columns for Analysis

        stock["Percent Change"] = stock[(f'Close', ticker)].pct_change().dropna()

            # Define strategy 

        stock["Strategy"] = 0

        # Condition 1: Close > VWAP and RSI < increasing from under 30 to over 30 and ADX > 25
        stock.loc[
            (stock["VWAP"] > stock[("Close", ticker)]) & (stock["RSI"].shift() < 30) & (stock["RSI"] > 30) & (stock["ADX"] > 25),
            "Strategy",
        ] = 1

        # Condition 2: VWAP is decreasing and Close < VWAP and RSI decreasing from 70 to below 70 
        stock.loc[
            (stock["VWAP"] < stock[("Close", ticker)]) & (stock["RSI"].shift() > 70) & (stock["RSI"] < 70) & (stock["ADX"] > 25),
            "Strategy",
        ] = -1

           

        stock['Strategy Return'] = stock['Strategy'].shift(1) * stock['Percent Change']
        stock['Strategy Return'].fillna(0, inplace=True)

        # need to create a position 

        # Start with an initial capital of £5000

        initial_capital = 5000

        stock["Capital"] = (initial_capital * (1 + stock['Strategy Return']).cumprod())
        
        # Calculate capital over time

        #end_of_day_capital = stock['Capital'].iloc[-1]
        #total_return (end_of_day_capital - initial_capital) / initial_capital


        analysis_df = pd.concat([analysis_df, stock], ignore_index=True)



        return analysis_df
    

    def test_1_day_news_strategy(self):

        analysis_df = pd.DataFrame()
        ticker = self.ticker
        stock = yf.download(self.ticker, start= self.start_date, end = self.end_date, interval="1d")
        stock.columns = stock.columns.to_flat_index()   

        ## Add Additional Columns for Analysis

        stock["Percent Change"] = stock[(f'Close', ticker)].pct_change().dropna()

        ## Generate market sentiment signal

        stock['Date'] = stock.index

        # will have to create loop here

        # Ensure 'Date' is in datetime format
        stock["Date"] = pd.to_datetime(stock["Date"])

        # Initialize an empty 'Sentiment' column
        #stock["Sentiment"] = NewsSentiment().returxsn_swing_news_sentiment()

        stock["Date"] = (stock["Date"].astype(str))
        print(stock.dtypes)
        stock["Sentiment"] = NewsSentiment(stock["Date"], ticker).return_swing_news_sentiment()

        #stock = stock.reset_index()
        # Define strategy 

        stock["Strategy"] = np.where(stock["Sentiment"] == "Buy", 1, 0)
        stock["Strategy"] = np.where(stock["Sentiment"] == "Sell", -1, 0)
        

        # Define strategy return

        stock['Strategy Return'] = stock['Strategy'].shift(1) * stock['Percent Change']
        stock['Strategy Return'].fillna(0, inplace=True)

        # capital and capital return

        initial_capital = 5000
        stock["Capital"] = (initial_capital * (1 + stock['Strategy Return']).cumprod())
        analysis_df = pd.concat([analysis_df, stock], ignore_index=True)




            
        

        return analysis_df
    

if __name__ == "__main__":
    backtester = Backtest("TSLA", "2024-09-01", 17,"2024-11-25" )
    news_strategy_df = backtester.test_1_day_news_strategy()    
        

          
    





  



