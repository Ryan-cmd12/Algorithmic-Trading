from abc import ABC, abstractmethod
from base.engine.events import FillEvent

class ExecutionHandler(ABC):
    @abstractmethod
    def execute_order(self,event):
        raise NotImplementedError('please implement execute_order()')
    
class SimulatedExecutionHander(ExecutionHandler):
    def __init__(self,events,data_handler, commission = 0.99):
        self.events = events
        self.data_handler = data_handler
        self.commission = commission
    def execute_order(self, order_event):
        symbol = order_event.symbol
        qty = order_event.quantity
        direction = order_event.direction
        timeindex = self.data_handler.current_date
        fill_price = self.data_handler.get_latest_bar_value(symbol)

        fill = FillEvent(
            timeindex=timeindex,
            symbol=symbol,
            quantity=qty,
            direction=direction,
            fill_cost=fill_price,
            commission=self.commission
        )

        self.events.put(fill)
        print(f"Filled:{direction} {qty} of {symbol} at {fill_price}, commission fee:{self.commission}")