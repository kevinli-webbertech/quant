import yfinance as yf
import datetime

vix_ticker = yf.Ticker("^VIX")
today = datetime.date.today().strftime('%Y-%m-%d')
vix_data = vix_ticker.history(start="1900-01-01", end=today)

print(vix_data.tail())