import pandas as pd
import yfinance as yf
import talib
import backtrader as bt

# ✅ Custom Data Feed with RSI
class PandasDataRSI(bt.feeds.PandasData):
    lines = ('rsi',)
    params = (('rsi', -1),)

# ✅ RSI Strategy
class RSIStrategy(bt.Strategy):
    params = dict(initial_cash=10000)

    def __init__(self):
        self.cash = self.p.initial_cash
        self.shares = 0
        self.trade_size = 20
        self.trades = []

    def next(self):
        price = self.data.close[0]
        rsi = self.data.rsi[0]
        date = self.data.datetime.date(0)
        value = self.cash + self.shares * price

        if rsi < 30 and self.cash >= price * self.trade_size:
            self.shares += self.trade_size
            self.cash -= price * self.trade_size
            self.trades.append(f"✅ BUY on {date}, Price: {price:.2f}, Portfolio: ${value:.2f}")

        elif rsi > 70 and self.shares >= self.trade_size:
            self.shares -= self.trade_size
            self.cash += price * self.trade_size
            self.trades.append(f"❌ SELL on {date}, Price: {price:.2f}, Portfolio: ${value:.2f}")

    def stop(self):
        final_value = self.cash + self.shares * self.data.close[0]
        self.trades.append(f"{self.data._name}: {final_value:.2f}")
        self.final_value = final_value

# ✅ Safe RSI calculation and data prep
def fetch_rsi_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError("No data")

    # Flatten column names if multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col) for col in df.columns]

    # Use the first column containing 'Close' as the close price
    close_cols = [col for col in df.columns if "Close" in col]
    if not close_cols:
        raise ValueError("No close column found")

    df['Close'] = df[close_cols[0]].ffill()
    df.dropna(subset=['Close'], inplace=True)

    # ✅ Proper 1D array for RSI with index matching
    rsi = talib.RSI(df['Close'].astype(float).values.flatten(), timeperiod=14)
    df = df.assign(rsi=pd.Series(rsi, index=df.index))
    df.dropna(inplace=True)

    return df

# ✅ Run single ticker backtest
def run_rsi_backtest(ticker, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):
    try:
        df = fetch_rsi_data(ticker, start_date, end_date)
        data = PandasDataRSI(dataname=df, name=ticker)

        cerebro = bt.Cerebro()
        cerebro.addstrategy(RSIStrategy, initial_cash=initial_cash)
        cerebro.adddata(data)
        result = cerebro.run()
        strat = result[0]

        return strat.final_value, strat.trades

    except Exception as e:
        print(f"❌ Error for {ticker}: {e}")
        return None, []

# ✅ Batch Backtest with Pretty Output
def batch_rsi_backtest(groups, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):
    all_logs = []
    summary = ["\n## RSI Indicator"]

    for group_name, tickers in groups.items():
        print(f"\n📊 {group_name}")
        summary.append(group_name)

        for ticker in tickers:
            display_name = ticker.upper()
            final_value, logs = run_rsi_backtest(ticker, start_date, end_date, initial_cash)
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

# ✅ Main Run
if __name__ == "__main__":
    ticker_groups = {
        "Group 1": ["AAPL", "GOOG", "MSFT"],
        "Group2": ["SNOW", "ZM"],
        "Group3": ["NIO"],
        "Group4": ["TSLA"]
    }

    batch_rsi_backtest(ticker_groups)
