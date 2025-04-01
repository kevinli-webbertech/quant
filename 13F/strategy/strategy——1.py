import yfinance as yf
import matplotlib.pyplot as plt

data = yf.download("VOO", period="10y", interval="1d")
data.dropna(inplace=True)

ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
macd = ema_12 - ema_26
signal = macd.ewm(span=9, adjust=False).mean()
data['MACD'] = macd
data['MACD_signal'] = signal
data['DMA_5'] = data['Close'].rolling(window=5).mean()
data['DMA_20'] = data['Close'].rolling(window=20).mean()
signals = []

for i in range(1, len(data)):
    try:
        macd_prev = float(data['MACD'].iloc[i - 1])
        signal_prev = float(data['MACD_signal'].iloc[i - 1])
        macd_curr = float(data['MACD'].iloc[i])
        signal_curr = float(data['MACD_signal'].iloc[i])
        macd_crossover = macd_prev < signal_prev and macd_curr > signal_curr
        dma5_prev = float(data['DMA_5'].iloc[i - 1])
        dma20_prev = float(data['DMA_20'].iloc[i - 1])
        dma5_curr = float(data['DMA_5'].iloc[i])
        dma20_curr = float(data['DMA_20'].iloc[i])
        dma_crossover = dma5_prev < dma20_prev and dma5_curr > dma20_curr
        vol_today = float(data['Volume'].iloc[i])
        vol_yesterday = float(data['Volume'].iloc[i - 1])
        vol_surge = vol_today > 2 * vol_yesterday

        if macd_crossover and dma_crossover and vol_surge:
            signals.append(data.index[i])
    except:
        continue

plt.figure(figsize=(14, 6))
plt.plot(data.index, data['Close'], label='Close Price', lw=1.5)

if signals:
    for signal_date in signals:
        price = data.loc[signal_date, 'Close']
        plt.plot(signal_date, price, marker='^', color='red', markersize=10)

    plt.title("VOO Strategy Signal (5Y Daily) - MACD + DMA + Volume Surge")
    plt.legend(["Close Price", "Signal"])
else:
    plt.title("VOO Strategy (5Y Daily) - No Signal Found")
    plt.text(data.index[int(len(data) * 0.5)], data['Close'].max() * 0.95,
             'No signal found matching strategy.',
             fontsize=12, color='gray', ha='center')

plt.xlabel("Date")
plt.ylabel("Close Price")
plt.grid(True)
plt.tight_layout()
plt.show()

if signals:
    print("满足策略的信号日期如下（共", len(signals), "次）：")
    for d in signals:
        print(d.strftime("%Y-%m-%d"))
else:
    print("没有找到符合 MACD 金叉 + DMA 金叉 + Volume 翻倍 的日期信号。")

