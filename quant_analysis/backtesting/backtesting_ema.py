import pandas as pd
import yfinance as yf
import talib
import backtrader as bt

# ✅ Custom EMA Data Feed
class PandasDataEMA(bt.feeds.PandasData):
    lines = ('ema_20',)
    params = (('ema_20', -1),)

# ✅ EMA Strategy with Crossover and Logging
class EMAStrategy(bt.Strategy):
    params = dict(initial_cash=10000)

    def __init__(self):
        self.ema_cross = bt.indicators.CrossOver(self.data.close, self.data.ema_20)
        self.cash = self.p.initial_cash
        self.shares = 0
        self.trade_size = 20

    def next(self):
        price = self.data.close[0]
        portfolio_value = self.cash + self.shares * price

        if self.ema_cross > 0:
            if self.cash >= price * self.trade_size:
                self.shares += self.trade_size
                self.cash -= price * self.trade_size
                print(f"✅ BUY on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")
        elif self.ema_cross < 0:
            if self.shares >= self.trade_size:
                self.shares -= self.trade_size
                self.cash += price * self.trade_size
                print(f"❌ SELL on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

    def stop(self):
        self.final_value = self.cash + self.shares * self.data.close[0]

# ✅ Run EMA Strategy for a Single Ticker
def run_ema_backtest(ticker, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns.values]

        close_cols = [col for col in df.columns if 'Close' in col]
        if not close_cols:
            print(f"❌ No close column for {ticker}")
            return None

        df['Close'] = df[close_cols[0]].ffill()
        df.dropna(subset=['Close'], inplace=True)

        df['ema_20'] = pd.Series(talib.EMA(df['Close'].astype(float).values.ravel(), timeperiod=20), index=df.index)
        df.dropna(inplace=True)

        data_feed = PandasDataEMA(dataname=df)

        cerebro = bt.Cerebro()
        cerebro.addstrategy(EMAStrategy, initial_cash=initial_cash)
        cerebro.adddata(data_feed)
        cerebro.run()

        strat = cerebro.runstrats[0][0]
        return round(strat.final_value, 2)

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")
        return None

# ✅ Group EMA Backtest with Summary Output
def batch_ema_backtest(groups, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):

    results = {}
    summary_lines = ["\n## EMA Indicator"]

    for group_name, tickers in groups.items():
        print(group_name)
        summary_lines.append(group_name)

        group_result = {}
        for ticker in tickers:
            display_name = ticker.upper()
            final_value = run_ema_backtest(ticker, start_date, end_date, initial_cash)

            if final_value is not None:
                print(f"{display_name}: {final_value:.2f}")
                summary_lines.append(f"{display_name}: {final_value:.2f}")
                group_result[display_name] = final_value
            else:
                print(f"{display_name}: ❌ Failed")
                summary_lines.append(f"{display_name}: ❌ Failed")
                group_result[display_name] = "Error"

        print()
        summary_lines.append("")
        results[group_name] = group_result

    print("\n".join(summary_lines))
    return results

# ✅ Example Usage
if __name__ == "__main__":
    ticker_groups = {
        "Group 1": ["AAPL", "GOOG", "MSFT"],
        "Group2": ["SNOW", "ZM"],
        "Group3": ["NIO"],
        "Group4": ["TSLA"]
    }

    ema_results = batch_ema_backtest(
        ticker_groups,
        start_date="2020-01-01",
        end_date="2025-03-14",
        initial_cash=10000
    )
