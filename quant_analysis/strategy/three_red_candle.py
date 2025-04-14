import yfinance as yf
import pandas as pd
from datetime import datetime

def generate_trade_signals(df):
    df = df.copy()

    # Calculate 200-day average volume as a Series
    avg_vol_200 = df['Volume'].rolling(window=200).mean()

    # Define down candles
    df['is_down'] = df['Close'] < df['Open']

    # Check for 3 consecutive down candles
    df['three_down'] = df['is_down'] & df['is_down'].shift(1) & df['is_down'].shift(2)

    # Volume trend: up or down for the last 3 candles
    df['vol_up'] = df['Volume'] > df['Volume'].shift(1)
    df['vol_up2'] = df['Volume'].shift(1) > df['Volume'].shift(2)
    df['vol_down'] = df['Volume'] < df['Volume'].shift(1)
    df['vol_down2'] = df['Volume'].shift(1) < df['Volume'].shift(2)

    # All 3 volumes must be above their 200-day average
    vol1_above_avg = df['Volume'] > avg_vol_200
    vol2_above_avg = df['Volume'].shift(1) > avg_vol_200.shift(1)
    vol3_above_avg = df['Volume'].shift(2) > avg_vol_200.shift(2)

    df['vol_all_above_avg'] = vol1_above_avg & vol2_above_avg & vol3_above_avg

    # Initialize signal column
    df['signal'] = None

    # SELL condition
    df.loc[
        df['three_down'] &
        df['vol_up'] & df['vol_up2'] &
        df['vol_all_above_avg'],
        'signal'
    ] = 'SELL'

    # BUY condition
    df.loc[
        df['three_down'] &
        df['vol_down'] & df['vol_down2'] &
        df['vol_all_above_avg'],
        'signal'
    ] = 'BUY'

    # Attach the avg volume for display if needed
    df['avg_vol_200'] = avg_vol_200

    return df[['Open', 'High', 'Low', 'Close', 'Volume', 'avg_vol_200', 'signal']]

def check_for_signals(ticker, interval, period):
    df = yf.download(tickers=ticker, interval=interval, period=period, progress=False)

    if df.empty or len(df) < 200:
        print(f"[{datetime.now()}] {ticker}: Not enough data to check signals.")
        return

    signals_df = generate_trade_signals(df)
    signal_rows = signals_df[signals_df['signal'].notnull()]

    if not signal_rows.empty:
        print(f"\n[{datetime.now()}] 📣 Found {len(signal_rows)} signal(s) for {ticker}!\n")
        print(signal_rows)
    else:
        print(f"[{datetime.now()}] {ticker}: No signals found in the past {period}.")

# ✅ Run the signal check
check_for_signals(
    ticker='AAPL',
    interval='1d',
    period='1y'
)