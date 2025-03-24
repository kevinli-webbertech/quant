import pandas as pd
import yfinance as yf
import talib
import backtrader as bt

# ✅ Step 1: Download Data
ticker = "GOOG"
df = yf.download(ticker, start="2020-01-01", end="2025-03-14", auto_adjust=False)

# ✅ Step 2: Ensure 'Close' Column Exists
if isinstance(df.columns, pd.MultiIndex):
    df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df.columns]

df.rename(columns={'Close_GOOG': 'Close'}, inplace=True)

print("Updated Columns in DataFrame:", df.columns.tolist())  # Debugging

if 'Close' not in df.columns:
    print("❌ 'Close' column not found! Exiting.")
    exit()

df['Close'] = df['Close'].ffill()
df.dropna(subset=['Close'], inplace=True)

# ✅ Step 3: Compute MACD (Ensuring 1D NumPy Format)
df['macd'], df['signal'], df['hist'] = talib.MACD(df['Close'].astype(float).values.ravel(),
                                                  fastperiod=12, slowperiod=26, signalperiod=9)

# ✅ Step 4: Drop NaN Values to Prevent Index Issues
df.dropna(inplace=True)

# ✅ Step 5: Define Backtrader Data Feed (Now Includes `macd`, `signal`, `hist`)
class PandasDataMACD(bt.feeds.PandasData):
    lines = ('macd', 'signal', 'hist')
    params = (('macd', -1), ('signal', -1), ('hist', -1))

# ✅ Step 6: Define MACD Strategy with Fixed 20-Share Trades
class MACDStrategy(bt.Strategy):
    initial_cash = 10000  # Start with $10,000
    cash = initial_cash
    shares = 0
    trade_size = 20  # Always trade 20 shares

    def __init__(self):
        self.macd_cross = bt.indicators.CrossOver(self.data.macd, self.data.signal)

    def next(self):
        price = self.data.close[0]
        portfolio_value = self.cash + (self.shares * price)  # ✅ Real-time Portfolio Value

        if self.macd_cross > 0:  # BUY SIGNAL
            if self.cash >= price * self.trade_size:
                self.shares += self.trade_size
                self.cash -= price * self.trade_size
                print(f"✅ BUY on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

        elif self.macd_cross < 0:  # SELL SIGNAL
            if self.shares >= self.trade_size:
                self.shares -= self.trade_size
                self.cash += price * self.trade_size
                print(f"❌ SELL on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

    def stop(self):
        final_value = self.cash + (self.shares * self.data.close[0])
        print(f"🔹 Final Portfolio Value (MACD Strategy) on 2025-03-14: ${final_value:.2f}")

# ✅ Step 7: Run Backtrader Simulation
cerebro = bt.Cerebro()
cerebro.addstrategy(MACDStrategy)
data = PandasDataMACD(dataname=df)
cerebro.adddata(data)
cerebro.run()
