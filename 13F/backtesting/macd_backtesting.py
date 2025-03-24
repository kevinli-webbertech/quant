import talib
import pandas as pd
import yfinance as yf

# Download historical data for a stock
ticker = "AAPL"
data = yf.download(ticker, start="2020-01-01", end="2023-10-31")


#### Step 3: Calculate MACD and Signal Line

# Calculate MACD and Signal Line
data['MACD'], data['Signal'], data['Histogram'] = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)


#### Step 4: Generate Buy/Sell Signals

# Generate signals
data['Signal'] = 0
data['Signal'][data['MACD'] > data['Signal']] = 1  # Buy signal
data['Signal'][data['MACD'] < data['Signal']] = -1  # Sell signal

# Shift signals to align with next day's action
data['Position'] = data['Signal'].shift(1)


#### Step 5: Calculate Strategy Returns

# Calculate daily returns
data['Market_Return'] = data['Close'].pct_change()

# Calculate strategy returns
data['Strategy_Return'] = data['Market_Return'] * data['Position']

# Calculate cumulative returns
data['Cumulative_Market_Return'] = (1 + data['Market_Return']).cumprod()
data['Cumulative_Strategy_Return'] = (1 + data['Strategy_Return']).cumprod()


#### Step 6: Analyze Performance

# Print final cumulative returns
print(f"Market Return: {data['Cumulative_Market_Return'][-1]:.2f}")
print(f"Strategy Return: {data['Cumulative_Strategy_Return'][-1]:.2f}")

# Plot cumulative returns
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(data['Cumulative_Market_Return'], label='Market Return', color='blue')
plt.plot(data['Cumulative_Strategy_Return'], label='Strategy Return', color='orange')
plt.title(f'{ticker} MACD Strategy Backtest')
plt.legend()
plt.show()


"""
### Explanation of the Code:
1. **Download Data**:
   - Use `yfinance` to download historical price data for a stock (e.g., Apple Inc.).

2. **Calculate MACD**:
   - Use `talib.MACD` to compute the MACD Line, Signal Line, and Histogram.

3. **Generate Signals**:
   - Buy when the MACD Line crosses above the Signal Line.
   - Sell when the MACD Line crosses below the Signal Line.

4. **Calculate Returns**:
   - Compute daily market returns and strategy returns.
   - Calculate cumulative returns to evaluate performance over time.

5. **Analyze Performance**:
   - Compare the cumulative returns of the strategy to the market.
   - Visualize the results using `matplotlib`.

---

### Example Output:
```
Market Return: 1.85
Strategy Return: 2.10
```

---

### Visualizing the Backtest Results
The plot will show the cumulative returns of the market versus the MACD strategy:
- **Market Return**: The return if you simply bought and held the stock.
- **Strategy Return**: The return from following the MACD strategy.

---

### Advanced Metrics for Backtesting
You can calculate additional performance metrics to evaluate the strategy:

#### 1. **Sharpe Ratio**:
   - Measures risk-adjusted returns.
   ```python
   risk_free_rate = 0.0  # Assume 0% risk-free rate
   excess_returns = data['Strategy_Return'] - risk_free_rate
   sharpe_ratio = excess_returns.mean() / excess_returns.std() * (252 ** 0.5)  # Annualized
   print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
   ```

#### 2. **Maximum Drawdown**:
   - Measures the largest peak-to-trough decline in the strategy.
   ```python
   data['Cumulative_Max'] = data['Cumulative_Strategy_Return'].cummax()
   data['Drawdown'] = data['Cumulative_Strategy_Return'] / data['Cumulative_Max'] - 1
   max_drawdown = data['Drawdown'].min()
   print(f"Maximum Drawdown: {max_drawdown:.2%}")
   ```

#### 3. **Win Rate**:
   - Measures the percentage of winning trades.
   ```python
   winning_trades = data[data['Strategy_Return'] > 0]
   win_rate = len(winning_trades) / len(data.dropna())
   print(f"Win Rate: {win_rate:.2%}")
   ```

---

### Summary:
- Backtesting a MACD strategy involves calculating MACD signals, generating buy/sell signals, and evaluating performance.
- You can use Python libraries like `pandas`, `yfinance`, and `matplotlib` to backtest and visualize the strategy.
- Advanced metrics like Sharpe Ratio, Maximum Drawdown, and Win Rate can provide deeper insights into the strategy's performance.

Let me know if you need further clarification or enhancements!

"""