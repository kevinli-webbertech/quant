import yfinance as yf
import pandas as pd
from datetime import datetime

def generate_trade_signals(df):
    df = df.copy()
    avg_vol_200 = df['Volume'].rolling(window=200).mean()

    df['is_down'] = df['Close'] < df['Open']
    df['three_down'] = df['is_down'] & df['is_down'].shift(1) & df['is_down'].shift(2)

    df['vol_up'] = df['Volume'] > df['Volume'].shift(1)
    df['vol_up2'] = df['Volume'].shift(1) > df['Volume'].shift(2)
    df['vol_down'] = df['Volume'] < df['Volume'].shift(1)
    df['vol_down2'] = df['Volume'].shift(1) < df['Volume'].shift(2)

    vol1_above_avg = df['Volume'] > avg_vol_200
    vol2_above_avg = df['Volume'].shift(1) > avg_vol_200.shift(1)
    vol3_above_avg = df['Volume'].shift(2) > avg_vol_200.shift(2)

    df['vol_all_above_avg'] = vol1_above_avg & vol2_above_avg & vol3_above_avg
    df['signal'] = None

    df.loc[df['three_down'] & df['vol_up'] & df['vol_up2'] & df['vol_all_above_avg'], 'signal'] = 'SELL'
    df.loc[df['three_down'] & df['vol_down'] & df['vol_down2'] & df['vol_all_above_avg'], 'signal'] = 'BUY'

    df['avg_vol_200'] = avg_vol_200
    return df[['Open', 'High', 'Low', 'Close', 'Volume', 'avg_vol_200', 'signal']]

def run_backtest(ticker, shares_per_trade=20, initial_shares=1000, initial_cash=100000):
    df = yf.download(
        ticker,
        start='2020-01-01',
        end=datetime.now().strftime('%Y-%m-%d'),
        interval='1d',
        auto_adjust=False,
        progress=False
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = df.columns.str.strip()

    required = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"\n❌ {ticker}: Missing columns {missing}")
        return None

    df = generate_trade_signals(df)
    signals = df[df['signal'].notnull()]

    if df.empty or len(df) < 1:
        print(f"\n⚠️ {ticker}: Not enough data.")
        return None

    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    cash = initial_cash
    shares = initial_shares
    initial_value = initial_cash + start_price * initial_shares
    trade_log = []

    for date, row in df.iterrows():
        signal = row['signal']
        price = row['Close']

        if isinstance(signal, str) and signal in ['BUY', 'SELL']:
            if signal == 'SELL' and shares >= shares_per_trade:
                cash += price * shares_per_trade
                shares -= shares_per_trade
                trade_log.append((date, 'SELL', price, cash, shares))
            elif signal == 'BUY' and cash >= price * shares_per_trade:
                cash -= price * shares_per_trade
                shares += shares_per_trade
                trade_log.append((date, 'BUY', price, cash, shares))

    final_value = cash + shares * end_price

    print(f"\n📊 {ticker} Summary")
    print(f"Initial: ${initial_value:,.2f} → Final: ${final_value:,.2f} | Change: {final_value - initial_value:+,.2f}")

    trade_df = pd.DataFrame(trade_log, columns=['Date', 'Action', 'Price', 'Cash', 'Shares Held'])
    if not trade_df.empty:
        print(f"\n📘 {ticker} Trade History:")
        print(trade_df.to_string(index=False))
    else:
        print(f"\n📘 {ticker} Trade History: No trades executed.")

    return {
        'ticker': ticker,
        'initial_value': initial_value,
        'final_value': final_value,
        'trades': trade_df
    }

def backtest_grouped_stocks(grouped_tickers, shares_per_trade=20, initial_shares=1000, initial_cash=100000):
    for group_name, tickers in grouped_tickers.items():
        print(f"\n🟩🟩🟩 {group_name.upper()} 🟩🟩🟩")
        group_results = []

        for ticker in tickers:
            result = run_backtest(
                ticker,
                shares_per_trade=shares_per_trade,
                initial_shares=initial_shares,
                initial_cash=initial_cash
            )
            if result:
                group_results.append(result)

        # Group summary
        print(f"\n📦 {group_name} Portfolio Summary:")
        for r in group_results:
            change_pct = (r['final_value'] - r['initial_value']) / r['initial_value'] * 100
            print(f"{r['ticker']}: ${r['initial_value']:,.2f} → ${r['final_value']:,.2f} ({change_pct:+.2f}%)")

# ✅ Define your groups
grouped_stocks = {
    "Group 1: Big Tech": ['AAPL', 'GOOG', 'MSFT'],
    "Group 2: Growth Tech": ['SNOW', 'ZM'],
    "Group 3: EV China": ['NIO'],
    "Group 4: Tesla": ['TSLA']
}

# 🚀 Run grouped backtests
backtest_grouped_stocks(grouped_stocks)
