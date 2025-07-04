from abc import ABC, abstractmethod
import pandas as pd
from base.engine.events import SignalEvent
#short desc of each strategy for me 


class Strategy(ABC):
    @abstractmethod #makes sure all strategy subclasses has a calcsignals func
    def calculate_signals(self,event):
        raise NotImplementedError('please implement calculate signals()')
    

#using 5day SMA and 20 day SMA , buy when short-term crosses long-term(golden cross), sell when short-term below long-term(deathcross)
class MovingAverageCrossStrategy_SMA(Strategy):
    def __init__(self, data_handler, events, short_window=5, long_window=20):
        self.data_handler = data_handler
        self.symbols = self.data_handler.symbols
        self.bought = {symbol:False for symbol in self.symbols}
        self.events = events
        self.short_window = short_window
        self.long_window = long_window
    
    def calculate_signals(self,event):
        if event.type != 'MARKET':
            return
        
        for symbol in self.symbols:
            bars = self.data_handler.get_latest_bars(symbol, self.long_window)
            if len(bars) < self.long_window:
                continue
            prices = pd.Series(bar[1] for bar in bars) #getting price values
            short_ma = prices[-self.short_window:].mean()
            long_ma = prices.mean() #len of bar is longwindow already
            date_time = bars[-1][0]

            if short_ma > long_ma and not self.bought[symbol]:
                signal = SignalEvent(symbol, 'SMA_CROSS', date_time, 'BUY', 1.0)
                self.events.put(signal)
                self.bought[symbol] = True
                print(f"Buy Signal: {symbol} at {date_time}")

            if short_ma < long_ma and not self.bought[symbol]:
                signal = SignalEvent(symbol, 'SMA_CROSS', date_time, 'SELL', 1.0)
                self.events.put(signal)
                self.bought[symbol] = False
                print(f"Sell Signal: {symbol} at {date_time}")

        