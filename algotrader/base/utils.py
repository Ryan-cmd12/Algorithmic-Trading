from collections import defaultdict
from .models import Trade

def g_holdings(portfolio):
    holdings = defaultdict(int)
    trades = Trade.objects.filter(portfolio=portfolio)
    for trade in trades:
        if trade.trade_type == 'BUY':
            holdings[trade.stock] += trade.quantity
        elif trade.trade_type == 'SELL':
            holdings[trade.stock] -= trade.quantity
    holdings = {stock:qty for stock,qty in holdings.items() if qty >0}
    return holdings