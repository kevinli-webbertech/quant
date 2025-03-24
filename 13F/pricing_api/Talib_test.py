import yfinance as yf
import talib
import pandas as pd

# Download historical data for AAPL
ticker = "AAPL"
df = yf.download(ticker, start="2023-01-01", end="2023-10-31", auto_adjust=True)

# Make sure to flatten the 'Close' series to a 1D numpy array
close = df['Close'].to_numpy().flatten()

# Calculate MACD: returns MACD line, Signal line, and Histogram
macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

# Calculate RSI (14-period by default)
rsi = talib.RSI(close, timeperiod=14)

# Add the indicators to the DataFrame for easy viewing
df['MACD'] = macd
df['Signal'] = signal
df['Histogram'] = hist
df['RSI'] = rsi

# Display the last few rows with the calculated indicators
print(df[['Close', 'MACD', 'Signal', 'Histogram', 'RSI']].tail())

#fi
