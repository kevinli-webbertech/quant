import pandas as pd
import yfinance as yf
import talib
import backtrader as bt

# ✅ Step 1: Download Data
ticker = "NIO"
df = yf.download(ticker, start="2020-01-01", end="2025-03-14", auto_adjust=False)

# ✅ Step 2: Fix MultiIndex Column Issue
if isinstance(df.columns, pd.MultiIndex):
    df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df.columns]

df.rename(columns={'Close_NIO': 'Close'}, inplace=True)

print("Updated Columns in DataFrame:", df.columns.tolist())  # Debugging

if 'Close' not in df.columns:
    print("❌ 'Close' column not found! Exiting.")
    exit()

df['Close'] = df['Close'].ffill()
df.dropna(subset=['Close'], inplace=True)

# ✅ Step 3: Compute DMA (Displaced Moving Average)
df['dma_short'] = talib.SMA(df['Close'].astype(float).values.ravel(), timeperiod=10)
df['dma_long'] = talib.SMA(df['Close'].astype(float).values.ravel(), timeperiod=50)

# ✅ Shift SMA values forward to create DMA
df['dma_short'] = df['dma_short'].shift(5)  # 5-period displacement
df['dma_long'] = df['dma_long'].shift(10)   # 10-period displacement

# ✅ Drop NaN values due to shifting
df.dropna(inplace=True)

# ✅ Step 4: Define Backtrader Data Feed (Now Includes `dma_short` and `dma_long`)
class PandasDataDMA(bt.feeds.PandasData):
    lines = ('dma_short', 'dma_long')  # Add short & long DMA as new lines
    params = (('dma_short', -1), ('dma_long', -1))

# ✅ Step 5: Define DMA Strategy with Fixed 20-Share Trades
class DMAStrategy(bt.Strategy):
    initial_cash = 10000  # Start with $10,000
    cash = initial_cash
    shares = 0
    trade_size = 20  # Always trade 20 shares

    def __init__(self):
        self.dma_cross = bt.indicators.CrossOver(self.data.dma_short, self.data.dma_long)

    def next(self):
        price = self.data.close[0]

        if self.dma_cross > 0:  # BUY SIGNAL
            if self.cash >= price * self.trade_size:
                self.shares += self.trade_size
                self.cash -= price * self.trade_size
                print(f"✅ BUY on {self.data.datetime.date(0)}, Price: {price:.2f}, Cash Left: ${self.cash:.2f}, Shares: {self.shares}")

        elif self.dma_cross < 0:  # SELL SIGNAL
            if self.shares >= self.trade_size:
                self.shares -= self.trade_size
                self.cash += price * self.trade_size
                print(f"❌ SELL on {self.data.datetime.date(0)}, Price: {price:.2f}, Cash After Sale: ${self.cash:.2f}, Shares Left: {self.shares}")

    def stop(self):
        final_value = self.cash + (self.shares * self.data.close[0])
        print(f"🔹 Final Portfolio Value (DMA Strategy) on 2025-03-14: ${final_value:.2f}")

# ✅ Step 6: Run Backtrader Simulation
cerebro = bt.Cerebro()
cerebro.addstrategy(DMAStrategy)
data = PandasDataDMA(dataname=df)  # ✅ Use Custom Data Feed with DMA
cerebro.adddata(data)
cerebro.run()
