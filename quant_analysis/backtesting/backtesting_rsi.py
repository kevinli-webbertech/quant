import pandas as pd
import yfinance as yf
import talib
import backtrader as bt

# ✅ Step 1: Download Data
ticker = "NIO"
df = yf.download(ticker, start="2020-01-01", end="2025-03-14", auto_adjust=False)

# ✅ Step 2: Ensure 'Close' Column Exists
if isinstance(df.columns, pd.MultiIndex):
    df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df.columns]

df.rename(columns={'Close_NIO': 'Close'}, inplace=True)

print("Updated Columns in DataFrame:", df.columns.tolist())  # Debugging

if 'Close' not in df.columns:
    print("❌ 'Close' column not found! Exiting.")
    exit()

df['Close'] = df['Close'].ffill()
df.dropna(subset=['Close'], inplace=True)

# ✅ Step 3: Compute RSI (Ensuring 1D NumPy Format)
df['rsi'] = talib.RSI(df['Close'].astype(float).values.ravel(), timeperiod=14)

# ✅ Step 4: Drop NaN Values to Prevent Index Issues
df.dropna(inplace=True)

# ✅ Step 5: Define Backtrader Data Feed (Now Includes `rsi`)
class PandasDataRSI(bt.feeds.PandasData):
    lines = ('rsi',)
    params = (('rsi', -1),)

# ✅ Step 6: Define RSI Strategy with Fixed 20-Share Trades
class RSIStrategy(bt.Strategy):
    initial_cash = 10000  # Start with $10,000
    cash = initial_cash
    shares = 0
    trade_size = 20  # Always trade 20 shares

    def __init__(self):
        pass

    def next(self):
        price = self.data.close[0]
        portfolio_value = self.cash + (self.shares * price)  # ✅ Real-time Portfolio Value

        if self.data.rsi[0] < 30:  # BUY SIGNAL (RSI oversold)
            if self.cash >= price * self.trade_size:
                self.shares += self.trade_size
                self.cash -= price * self.trade_size
                print(f"✅ BUY on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

        elif self.data.rsi[0] > 70:  # SELL SIGNAL (RSI overbought)
            if self.shares >= self.trade_size:
                self.shares -= self.trade_size
                self.cash += price * self.trade_size
                print(f"❌ SELL on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

    def stop(self):
        final_value = self.cash + (self.shares * self.data.close[0])
        print(f"🔹 Final Portfolio Value (RSI Strategy) on 2025-03-14: ${final_value:.2f}")

# ✅ Step 7: Run Backtrader Simulation
cerebro = bt.Cerebro()
cerebro.addstrategy(RSIStrategy)
data = PandasDataRSI(dataname=df)
cerebro.adddata(data)
cerebro.run()
