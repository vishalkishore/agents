import requests 
from dotenv import load_dotenv
import os
load_dotenv()

ALPHA_VANTAGE_API_KEY=os.getenv('ALPHA_VANTAGE_API_KEY')

def method():
    function='TIME_SERIES_INTRADAY'
    symbol='AAPL'
    interval='1min'
    url=f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={ALPHA_VANTAGE_API_KEY}'
    response=requests.get(url)
    data=response.json()
    print(data)