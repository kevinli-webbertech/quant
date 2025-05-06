import pandas as pd
import yfinance as yf
import talib
import backtrader as bt
import io
import sys

# ✅ Custom MACD Data Feed
class PandasDataMACD(bt.feeds.PandasData):
    lines = ('macd', 'signal', 'hist')
    params = (('macd', -1), ('signal', -1), ('hist', -1))

# ✅ Strategy with Buy/Sell Logging
class MACDStrategy(bt.Strategy):
    params = dict(initial_cash=10000)

    def __init__(self):
        self.macd_cross = bt.indicators.CrossOver(self.data.macd, self.data.signal)
        self.cash = self.p.initial_cash
        self.shares = 0
        self.trade_size = 20

    def next(self):
        price = self.data.close[0]
        portfolio_value = self.cash + (self.shares * price)

        if self.macd_cross > 0:
            if self.cash >= price * self.trade_size:
                self.shares += self.trade_size
                self.cash -= price * self.trade_size
                print(f"✅ BUY on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

        elif self.macd_cross < 0:
            if self.shares >= self.trade_size:
                self.shares -= self.trade_size
                self.cash += price * self.trade_size
                print(f"❌ SELL on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

    def stop(self):
        self.final_value = self.cash + (self.shares * self.data.close[0])

# ✅ Run MACD Backtest and Return Final Value
def run_macd_backtest_original(ticker, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns.values]

        close_cols = [col for col in df.columns if 'Close' in col]
        if not close_cols:
            print(f"❌ 'Close' column not found in data for {ticker}")
            return None

        df['Close'] = df[close_cols[0]].ffill()
        df.dropna(subset=['Close'], inplace=True)

        macd, signal, hist = talib.MACD(df['Close'].astype(float).values, fastperiod=12, slowperiod=26, signalperiod=9)
        df['macd'] = pd.Series(macd, index=df.index)
        df['signal'] = pd.Series(signal, index=df.index)
        df['hist'] = pd.Series(hist, index=df.index)
        df.dropna(inplace=True)

        data_feed = PandasDataMACD(dataname=df)
        cerebro = bt.Cerebro()
        cerebro.addstrategy(MACDStrategy, initial_cash=initial_cash)
        cerebro.adddata(data_feed)
        cerebro.run()

        strat = cerebro.runstrats[0][0]
        return round(strat.final_value, 2)

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")
        return None

# ✅ Batch Run with Live Logs + Final Summary Print
def batch_macd_backtest_original(groups, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):

    results = {}
    summary_lines = ["\n## MACD Indicator"]

    for group_name, tickers in groups.items():
        print(group_name)
        summary_lines.append(group_name)

        group_result = {}
        for ticker in tickers:
            display_name = ticker.upper()
            final_value = run_macd_backtest_original(ticker, start_date, end_date, initial_cash)
            if final_value is not None:
                print(f"{display_name}: {final_value:.2f}")
                summary_lines.append(f"{display_name}: {final_value:.2f}")
                group_result[display_name] = final_value
            else:
                print(f"{display_name}: ❌ Failed")
                summary_lines.append(f"{display_name}: ❌ Failed")
                group_result[display_name] = "Error"

        print()
        summary_lines.append("")  # Empty line between groups
        results[group_name] = group_result

    # ✅ Final Summary After All Trades
    print("\n".join(summary_lines))
    return results

# ✅ Define Your Groups Here
if __name__ == "__main__":
    ticker_groups = {
        "Group 1": ["AAPL", "GOOG", "MSFT"],
        "Group2": ["SNOW", "ZM"],
        "Group3": ["NIO"],
        "Group4": ["TSLA"]
    }

    macd_results = batch_macd_backtest_original(
        ticker_groups,
        start_date="2020-01-01",
        end_date="2025-03-14",
        initial_cash=10000
    )
