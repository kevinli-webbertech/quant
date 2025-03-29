import yfinance as yf
import numpy as np

def indicator_A(ticker, end_date=None):
    data = yf.download(ticker, start="2020-01-01", end="2025-03-14", auto_adjust=False)
    data['RedCandle'] = data['Close'] < data['Open']
    data['OpenDiff'] = data['Open'].diff()

    alerts = []

    for i in range(2, len(data)):
        window = data.iloc[i - 2:i + 1]
        red_candles = window['RedCandle'].all()
        open0 = float(window['Open'].iloc[0])
        open1 = float(window['Open'].iloc[1])
        open2 = float(window['Open'].iloc[2])
        volumn0 = float(window['Volume'].iloc[0])
        volumn1 = float(window['Volume'].iloc[1])
        volumn2 = float(window['Volume'].iloc[2])
        falling_opens = open2 < open1 and open1 < open0
        increasing_volume = volumn2 > volumn1 and volumn1 > volumn0

        if red_candles and falling_opens and increasing_volume:
            median_volume = np.median(data['Volume'].iloc[max(0, i - 200):i])
            ratio = volumn2 / median_volume if median_volume else None

            alerts.append({
                "date": window.index[2].strftime('%Y-%m-%d'),
                "volume": int(volumn2),
                "ticker": ticker,
                "volume_ratio": round(ratio, 2) if ratio else None
            })

    return alerts

alerts = indicator_A("VOO")
for alert in alerts:
    print(alert)
