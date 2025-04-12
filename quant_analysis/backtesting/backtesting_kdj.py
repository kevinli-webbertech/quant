import yfinance as yf
import pandas as pd
import backtrader as bt

def rename_ohlc_columns(df, ticker):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [f"{col[0]}_{col[1]}" for col in df.columns]
    col_map = {}
    for col in df.columns:
        if col.endswith(f"_{ticker}"):
            col_map[col] = col.replace(f"_{ticker}", "")
    df.rename(columns=col_map, inplace=True)
    return df

def add_kdj(df, n=9):
    low_min = df['Low'].rolling(window=n).min()
    high_max = df['High'].rolling(window=n).max()
    rsv = 100 * (df['Close'] - low_min) / (high_max - low_min + 1e-9)
    df['K'] = rsv.ewm(alpha=1/3).mean()
    df['D'] = df['K'].ewm(alpha=1/3).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df.dropna()

class PandasDataKDJ(bt.feeds.PandasData):
    lines = ('K', 'D', 'J')
    params = (('K', -1), ('D', -1), ('J', -1))

class MultiKDJStrategy(bt.Strategy):
    trade_size = 20

    def __init__(self):
        self.kdj_cross = {}
        self.cash = {}
        self.shares = {}
        for d in self.datas:
            self.kdj_cross[d._name] = bt.ind.CrossOver(d.K, d.D)
            self.cash[d._name] = 10000
            self.shares[d._name] = 0

    def next(self):
        for d in self.datas:
            symbol = d._name
            price = d.close[0]
            cross = self.kdj_cross[symbol][0]
            value = self.cash[symbol] + self.shares[symbol] * price

            if cross > 0 and self.cash[symbol] >= price * self.trade_size:
                self.shares[symbol] += self.trade_size
                self.cash[symbol] -= price * self.trade_size
                print(f"✅ BUY {symbol} | {d.datetime.date(0)} | ${price:.2f} | Portfolio: ${value:.2f}")

            elif cross < 0 and self.shares[symbol] >= self.trade_size:
                self.shares[symbol] -= self.trade_size
                self.cash[symbol] += price * self.trade_size
                print(f"❌ SELL {symbol} | {d.datetime.date(0)} | ${price:.2f} | Portfolio: ${value:.2f}")

    def stop(self):
        print("\n🔚 Final Portfolio Summary:")
        for d in self.datas:
            symbol = d._name
            final_value = self.cash[symbol] + self.shares[symbol] * d.close[0]
            print(f"📊 {symbol}: ${final_value:.2f}")

def run_multi_kdj_backtest(tickers):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiKDJStrategy)

    for ticker in tickers:
        print(f"\n📥 Downloading {ticker}...")
        df = yf.download(ticker, start="2020-01-01", end="2025-03-14", auto_adjust=False)

        if df.empty:
            print(f"⚠️ No data for {ticker}, skipping...")
            continue

        rename_ohlc_columns(df, ticker)

        if not all(c in df.columns for c in ['Open', 'High', 'Low', 'Close']):
            print(f"⚠️ Incomplete data for {ticker}, skipping...")
            continue

        df = df[['Open', 'High', 'Low', 'Close']].ffill().dropna()
        df = add_kdj(df)

        feed = PandasDataKDJ(dataname=df, name=ticker)
        cerebro.adddata(feed)

    cerebro.run()

tickers = ['KR', 'AON', 'V', 'LEN', 'MCO', 'LPX', 'CVX', 'DPZ', 'NVR', 'AAPL', 'COF', 'VRSN', 'CHTR', 'ALLY', 'KO', 'STZ', 'C']
run_multi_kdj_backtest(tickers)
