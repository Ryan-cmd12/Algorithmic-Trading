class Event:
    pass
class MarketEvent(Event):
    def __init__(self):
        self.type = 'MARKET'
class SignalEvent(Event):
    def __init__(self,symbol,strategy_id,datetime,signal_type,strength):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.strategy_id = strategy_id
        self.datetime= datetime
        self.signal_type = signal_type
        self.strength = strength
class OrderEvent(Event):
    def __init__(self,symbol,order_type,quantity, direction):
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type #'market or limit' MKT or LMT
        self.quantity = quantity
        self.direction = direction #(buy or sell)

    def printOrder(self):
        print(f'Order:{self.direction} {self.quantity} of {self.symbol} as a {self.order_type} order')

class FillEvent(Event): #describes cost of purchase or sale as well as transactional costs
    def __init__(self, timeindex, symbol, quantity, direction, fill_cost, commission=0.99):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        self.commission = commission #moomoos$0.99 per order
        
    