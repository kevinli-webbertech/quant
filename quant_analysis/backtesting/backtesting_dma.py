import pandas as pd
import yfinance as yf
import talib
import backtrader as bt

# ✅ Custom DMA Data Feed
class PandasDataDMA(bt.feeds.PandasData):
    lines = ('dma_short', 'dma_long')
    params = (('dma_short', -1), ('dma_long', -1))

# ✅ DMA Strategy with Trade Logs
class DMAStrategy(bt.Strategy):
    params = dict(initial_cash=10000)

    def __init__(self):
        self.dma_cross = bt.indicators.CrossOver(self.data.dma_short, self.data.dma_long)
        self.cash = self.p.initial_cash
        self.shares = 0
        self.trade_size = 20

    def next(self):
        price = self.data.close[0]
        portfolio_value = self.cash + (self.shares * price)

        if self.dma_cross > 0:
            if self.cash >= price * self.trade_size:
                self.shares += self.trade_size
                self.cash -= price * self.trade_size
                print(f"✅ BUY on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")
        elif self.dma_cross < 0:
            if self.shares >= self.trade_size:
                self.shares -= self.trade_size
                self.cash += price * self.trade_size
                print(f"❌ SELL on {self.data.datetime.date(0)}, Price: {price:.2f}, Portfolio: ${portfolio_value:.2f}")

    def stop(self):
        self.final_value = self.cash + self.shares * self.data.close[0]

# ✅ Original DMA Logic (Displaced SMA)
def run_dma_backtest(ticker, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns.values]

        close_cols = [col for col in df.columns if 'Close' in col]
        if not close_cols:
            print(f"❌ No 'Close' column found for {ticker}")
            return None

        df['Close'] = df[close_cols[0]].ffill()
        df.dropna(subset=['Close'], inplace=True)

        df['dma_short'] = talib.SMA(df['Close'].astype(float).values.ravel(), timeperiod=10)
        df['dma_long'] = talib.SMA(df['Close'].astype(float).values.ravel(), timeperiod=50)

        df['dma_short'] = pd.Series(df['dma_short'], index=df.index).shift(5)
        df['dma_long'] = pd.Series(df['dma_long'], index=df.index).shift(10)

        df.dropna(inplace=True)
        data_feed = PandasDataDMA(dataname=df)

        cerebro = bt.Cerebro()
        cerebro.addstrategy(DMAStrategy, initial_cash=initial_cash)
        cerebro.adddata(data_feed)
        cerebro.run()

        strat = cerebro.runstrats[0][0]
        return round(strat.final_value, 2)

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")
        return None

# ✅ Group DMA Backtest with Summary
def batch_dma_backtest(groups, start_date="2020-01-01", end_date="2025-03-14", initial_cash=10000):

    results = {}
    summary_lines = ["\n## DMA Indicator"]

    for group_name, tickers in groups.items():
        print(group_name)
        summary_lines.append(group_name)

        group_result = {}
        for ticker in tickers:
            display_name = ticker.upper()
            final_value = run_dma_backtest(ticker, start_date, end_date, initial_cash)

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

    dma_results = batch_dma_backtest(
        ticker_groups,
        start_date="2020-01-01",
        end_date="2025-03-14",
        initial_cash=10000
    )
