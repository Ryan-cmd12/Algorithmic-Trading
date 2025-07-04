from django.core.management.base import BaseCommand
from queue import Queue
from base.engine.data_handler import HistoricCSVDataHandler
from base.engine.strategy import MovingAverageCrossStrategy_SMA
from base.engine.Portfolio import Portfolio
from base.engine.events import MarketEvent
from base.engine.execution import SimulatedExecutionHander

class Command(BaseCommand):
    help = 'Runs the backtest'

    def handle(self, *args, **Kwargs):
        print('starting backtest...')

        initial_capital = 100000.0
        symbols = ['AAPL']

        events = Queue()
        data_handler = HistoricCSVDataHandler(events,symbols)
        strategy = MovingAverageCrossStrategy_SMA(data_handler,events)
        portfolio= Portfolio(data_handler,events,initial_capital)
        ExecutionHandler = SimulatedExecutionHander(events, data_handler)

        while data_handler.continue_backtest:
            data_handler.update_bars() #move bar one dau forward
            while not events.empty():
                event = events.get()

                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    portfolio.update_timeindex()
                
                elif event.type == 'SIGNAL':
                    portfolio.update_signal(event)
                elif event.type == 'ORDER':
                    ExecutionHandler.execute_order(event)
                elif event.type == 'FILL':
                    portfolio.update_fill(event)
        print('backtest complete')

        final_results = portfolio.all_holdings[-1]
        print(f"Date: {final_results['datetime'].date()}")
        print(f"Cash: {final_results['cash']}")
        print(f"Commission paid: {final_results['commission']}")
        print(f"Total net worth: {final_results['total']}")


