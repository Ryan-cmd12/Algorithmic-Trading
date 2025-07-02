from base.models import Stock,PriceHistory
from datetime import date
import pandas as pd
from datetime import timedelta
from collections import deque
from events import MarketEvent

class HistoricCSVDataHandler:
    def __init__(self,events, symbols): #events: event queue, symbols: list of tickers
        self.events = events
        self.symbols = symbols

        self.symbol_data = {}
        self.latest_symbol_data = {symbol:deque(maxlen=1000) for symbol in symbols} #get the latest data
        self.continue_backtest = True
        self.current_date = None
        
        self._load_data_from_db()
    
    def _load_data_from_db(self):
        for symbol in self.symbols:
            try:
                stock = Stock.objects.get(symbol = symbol)
                price_val = PriceHistory.objects.filter(stock=stock).order_by('date')
                df = pd.DataFrame.from_records(
                    price_val.values('date', 'price'), index='date'  #returns a dict with date as index
                )
                df.index = pd.to_datetime(df.index) #converts to real datetime objects
                self.symbol_data[symbol] = df
            except Stock.DoesNotExist:
                print(f'{stock} not found in db')
                self.symbol_data[symbol] = pd.DataFrame()  #assign empty frame
        all_dates = sorted(
            set(date 
                for df in self.symbol_data.values() 
                for date in df.index
            )
        ) #this gives a sorted list of all trading dates in database across all stocks
        self.all_dates = all_dates
        self.date_index = 0

    def update_bars(self): #advances simulation by one day and adds a marketevent
        if self.date_index >= len(self.all_dates):
            self.continue_backtest = False #reached last day
            return
        self.current_date = self.all_dates[self.date_index]
        self.date_index += 1
        for symbol in self.symbols:
            df = self.symbol_data[symbol]
            if self.current_date in df.index:
                row = df.loc[self.current_date]
                self.latest_symbol_data[symbol].append((self.current_date,row['price']))
        self.events.put(MarketEvent())
    def get_latest_bar(self,symbol):
        return self.latest_symbol_data[symbol][-1]
    def get_latest_bars(self,symbol,N=1):
        return list(self.latest_symbol_data[symbol][-N:])
    def get_latest_bar_datetime(self,symbol):
        return self.get_latest_bar(symbol)[0]
    def get_latest_bar_value(self,symbol):
        return self.get_latest_bar(symbol)[1]