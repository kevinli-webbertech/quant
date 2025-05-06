import pandas as pd
import yfinance as yf
import backtrader as bt

# === Rename OHLC Columns ===
def rename_ohlc_columns(df, ticker):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [f"{col[0]}_{col[1]}" for col in df.columns]
    col_map = {}
    for col in df.columns:
        if col.endswith(f"_{ticker}"):
            col_map[col] = col.replace(f"_{ticker}", "")
    df.rename(columns=col_map, inplace=True)
    return df

# === Add KDJ Columns ===
def add_kdj(df, n=9):
    low_min = df['Low'].rolling(window=n).min()
    high_max = df['High'].rolling(window=n).max()
    rsv = 100 * (df['Close'] - low_min) / (high_max - low_min + 1e-9)
    df['K'] = rsv.ewm(alpha=1/3).mean()
    df['D'] = df['K'].ewm(alpha=1/3).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df.dropna()

# === Custom Backtrader Data Feed ===
class PandasDataKDJ(bt.feeds.PandasData):
    lines = ('K', 'D', 'J')
    params = (('K', -1), ('D', -1), ('J', -1))

# === KDJ Strategy ===
class KDJStrategy(bt.Strategy):
    params = dict(initial_cash=10000)

    def __init__(self):
        self.kdj_cross = bt.ind.CrossOver(self.data.K, self.data.D)
        self.cash = self.p.initial_cash
        self.shares = 0
        self.trade_size = 20
        self.trades = []

    def next(self):
        price = self.data.close[0]
        portfolio_value = self.cash + self.shares * price
        date = self.data.datetime.date(0)

        if self.kdj_cross > 0 and self.cash >= price * self.trade_size:
            self.shares += self.trade_size
            self.cash -= price * self.trade_size
            self.trades.append(f"✅ BUY on {date}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")
        elif self.kdj_cross < 0 and self.shares >= self.trade_size:
            self.shares -= self.trade_size
            self.cash += price * self.trade_size
            self.trades.append(f"❌ SELL on {date}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

    def stop(self):
        self.final_value = self.cash + self.shares * self.data.close[0]
        self.trades.append(f"{self.data._name}: {self.final_value:.2f}")

# === Run KDJ Strategy on Single Ticker ===
def run_kdj_backtest(ticker, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
        if df.empty:
            return None, []

        rename_ohlc_columns(df, ticker)
        if not all(c in df.columns for c in ['Open', 'High', 'Low', 'Close']):
            return None, []

        df = df[['Open', 'High', 'Low', 'Close']].ffill().dropna()
        df = add_kdj(df)

        data = PandasDataKDJ(dataname=df, name=ticker)
        cerebro = bt.Cerebro()
        cerebro.addstrategy(KDJStrategy, initial_cash=initial_cash)
        cerebro.adddata(data)
        results = cerebro.run()
        strat = results[0]

        return strat.final_value, strat.trades

    except Exception as e:
        print(f"❌ Error for {ticker}: {e}")
        return None, []

# === Batch KDJ Backtest with Group Summary ===
def batch_kdj_backtest(groups, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):

    all_logs = []
    summary = ["\n## KDJ Indicator"]

    for group_name, tickers in groups.items():
        print(f"\n📊 {group_name}")
        summary.append(group_name)

        for ticker in tickers:
            display_name = ticker.upper()
            final_value, logs = run_kdj_backtest(ticker, start_date, end_date, initial_cash)
            all_logs.extend(logs)

            if final_value is not None:
                print(f"{display_name}: {round(final_value, 2)}")
                summary.append(f"{display_name}: {round(final_value, 2)}")
            else:
                print(f"{display_name}: ❌ Failed")
                summary.append(f"{display_name}: ❌ Failed")

        summary.append("")

    print("\n".join(all_logs))
    print("\n" + "\n".join(summary))
    return summary

# === Example Run ===
if __name__ == "__main__":
    ticker_groups = {
        "Group 1": ["AAPL", "GOOG", "MSFT"],
        "Group2": ["SNOW", "ZM"],
        "Group3": ["NIO"],
        "Group4": ["TSLA"]
    }

    batch_kdj_backtest(ticker_groups)
