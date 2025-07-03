from events import OrderEvent, FillEvent
from collections import defaultdict
import datetime

class Portfolio:
    def __init__(self, data_handler, events, initial_capital= 100000.0):
        self.data_handler = data_handler
        self.events = events
        self.initial_capital = initial_capital
        self.symbols = data_handler.symbols
        
        self.curr_positions = {symbol:0 for symbol in self.symbols}
        self.curr_holdings = {
            'cash' : self.initial_capital,
            'commission': 0.0,
            'total': self.initial_capital
        }

        self.all_positions = [] #list of dicts of stock : qty owned at each time interval
        self.all_holdings = [] #list of dicts with cash/total/equity/commission paid thus far
    
    def update_timeindex(self):
        dt = self.data_handler.current_date #update dt w curr date

        position = {symbol: self.current_positions[symbol] for symbol in self.symbols}
        position['datetime'] = dt
        self.all_positions.append(position)

        holdings = {
            'datetime' :dt,
            'cash' : self.curr_holdings['cash'],
            'commission' : self.current_holdings['commission'],
            'total'  : 0.0, #initialised as 0, added below
        }

        for symbol in self.symbols:
            market_value = self.current_positions[symbol] * self.data_handler.get_latest_bar_value[symbol]
            holdings[symbol] = market_value
            holdings['total'] += market_value
        
        holdings['total'] += holdings['cash']
        self.all_holdings.append(holdings)

    def update_signal(self, signal): #create an orderevent n put it on queue
        order = None
        symbol = signal.symbol
        direction = self.signal_type.upper()
        strength = self.strength

        market_qty = 100
        curr_price = self.data_handler.get_latest_bar_value(symbol)
        
        if direction == 'BUY':
            order = OrderEvent(symbol=symbol, order_type='MKT', quantity=market_qty, direction='BUY')
        elif direction == 'SELL':
            order = OrderEvent(symbol=symbol, order_type='MKT', quantity=market_qty, direction='SELL')

        if order:
            self.events.put(order)
            print(f'Order created: {order.direction} {order.quantity} of {symbol} at {round(curr_price,2)}')
    
    def update_fill(self,fill):
        symbol = fill.symbol
        if fill.direction == 'BUY':
            fill_dir = 1
        else:
            fill_dir = -1
        qty = fill.quantity
        fill_cost = fill.fill_cost
        cost = fill_cost * qty
        commission = fill.commission

        self.curr_positions[symbol] += fill.dir * qty

        self.curr_holdings['cash'] -= (cost + commission) * fill_dir
        self.curr_holdings['commission'] += commission
