import datetime, requests
import pandas as pd
import alpaca_trade_api as alpaca
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="passwords.env")

# Initialize OpenAI client with your key
class NewsSentiment():

    def __init__(self, start_date, ticker):
            self.start_date = start_date
            self.ticker = ticker

    def return_news_sentiment(self):

        openai_api_key = os.getenv("OPENAI_API_KEY")  # For the OpenAI client
        api_key = os.getenv("API_KEY")                # Another API key
        secret_key = os.getenv("SECRET_KEY")
        client = OpenAI(api_key=openai_api_key) 
        api = alpaca.REST(api_key, secret_key, 'https://paper-api.alpaca.markets')
        start_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d").date()
        start_date_minus_one = start_date - datetime.timedelta(days=1)
        news = api.get_news(self.ticker, start = f"{start_date_minus_one}T21:00:00Z", end =f"{start_date}T14:30:00Z")

        stories_list = []

        for story in news:

            stories_list.append((story.summary))

        # Step 2: Prepare the prompt
        prompt = f"Here is a list of some important stories before market opening. Tell me what I should do with {self.ticker} stock. :\n\n{stories_list}\n\nReturn one word only: Buy, Sell, or Neutral."
        #prompt = f"Here is a list of some important stories before market opening. Tell me what I should do with Tesla stock. :\n\n{stories_list}\n\nExplain why. Then return one word only: Buy, Sell, or Neutral."


        # Step 3: Send the prompt to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )


        answer = response.choices[0].message.content
        print(f"Stories List = {stories_list}")
        print(f"Answer = {answer}")
        return answer
    
    def return_swing_news_sentiment(self):

        openai_api_key = os.getenv("OPENAI_API_KEY")  # For the OpenAI client
        api_key = os.getenv("API_KEY")                # Another API key
        secret_key = os.getenv("SECRET_KEY")
        client = OpenAI(api_key=openai_api_key) 
        api = alpaca.REST(api_key, secret_key, 'https://paper-api.alpaca.markets')
        self.start_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
        start_date_minus_4 = self.start_date - datetime.timedelta(days=4)
        self.start_date = self.start_date.strftime('%Y-%m-%d')
        start_date_minus_4 = start_date_minus_4.strftime('%Y-%m-%d')
        news = api.get_news(self.ticker, start = start_date_minus_4, end = self.start_date)

        stories_list = []

        for story in news:

            stories_list.append((story.summary))

        # Step 2: Prepare the prompt
        #prompt = f"Here is a list of some important stories before market opening. Tell me what I should do with {self.ticker} stock. :\n\n{stories_list}\n\n. Be intelligent, really tell me what you think will happen with the stock, only based on these stories. Return one word only: Buy, Sell, or Neutral."
        prompt = f"Here is a list of some important stories before market opening. Tell me what I should do with {self.ticker} stock. :\n\n{stories_list}\n\n. Be intelligent, really tell me what you think will happen with the stock, only based on these stories. Return: Buy, Sell, or Neutral and explain why"


        # Step 3: Send the prompt to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )


        answer = response.choices[0].message.content

        print(stories_list)
        return answer
    
if __name__ == "__main__":
    news_sentiment = NewsSentiment("2024-11-10","TSLA" )
    response = news_sentiment.return_swing_news_sentiment() 
    print(response)




