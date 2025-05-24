import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from pybit.unified_trading import HTTP

class CandlestickChart:
    def __init__(self, name='BTC/USDT',symbol='BTCUSDT', category="spot", start_time='', end_time='', interval='60', days=7):
        self.session = HTTP(testnet=False)
        if start_time == "":
            self.start_time = int(datetime.timestamp(datetime.now() - timedelta(days=days))) * 1000
        else:
            self.start_time = start_time

        if end_time == "":
            self.end_time = int(datetime.timestamp(datetime.now())) * 1000
        else:
            self.end_time = end_time
        self.sym_name = name
        self.category = category
        self.symbol = symbol
        self.interval = interval
        self.candles = self.get_candles()

    def get_candles(self):
        data = self.session.get_kline(
            category=self.category,
            symbol=self.symbol,
            interval=self.interval,
            start=self.start_time,
            end=self.end_time,
        )
        if data["retCode"] != 0:
            raise Exception(f"Error fetching data: {data['retMsg']}")
        candles = data["result"]["list"]
        if not candles:
            raise Exception("No available data to display.")
        candles.reverse()
        return candles

    def plot(self):
        open_times = [datetime.fromtimestamp(float(candle[0]) / 1000) for candle in self.candles]
        opens = [float(candle[1]) for candle in self.candles]
        highs = [float(candle[2]) for candle in self.candles]
        lows = [float(candle[3]) for candle in self.candles]
        closes = [float(candle[4]) for candle in self.candles]
        volumes = [float(candle[5]) for candle in self.candles]

        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0b1619')
        fig.canvas.manager.set_window_title(f'{self.sym_name} Kline')
        indices = np.arange(len(self.candles))
        width = 0.4

        for i in indices:
            color = 'green' if closes[i] >= opens[i] else 'red'
            ax.plot([i, i], [lows[i], highs[i]], color='white')  
            ax.add_patch(plt.Rectangle((i - width / 2, opens[i]), width, closes[i] - opens[i], color=color))

        ax.set_facecolor('#0b1619')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='x', colors='white')  
        ax.tick_params(axis='y', colors='white')  
        ax.set_xticks(indices[::max(1, len(indices) // 10)])
        ax.set_xticklabels([dt.strftime('%Y-%m-%d %H:%M') for dt in open_times[::max(1, len(indices) // 10)]], 
                        rotation=45, ha='right', color='white')
        ax.set_title(f'Candlestick {self.sym_name}', color='white')
        ax.set_xlabel('Time', color='white')  
        ax.set_ylabel('Price', color='white')  
        plt.grid(True, color='gray')

        ax2 = ax.twinx()
        ax2.bar(indices, volumes, color='orange', alpha=0.3, width=0.4, label='Volume')
        ax2.set_ylabel('Volume', color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')
        ax2.spines['right'].set_color('orange')

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":  
    chart = CandlestickChart(symbol="ETHUSDT")
    chart.plot()
