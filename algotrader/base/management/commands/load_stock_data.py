from django.core.management.base import BaseCommand
from base.models import Stock, PriceHistory
import yfinance as yf
from datetime import datetime
import pandas as pd


class Command(BaseCommand):
    
    help = 'Loads historical data for a list of stocks through yfinance'
    
    def handle(self, *args, **kwargs):
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        try:
            df = pd.read_html(url)[0]
        except Exception as e:
            print(f'error loading {e}')
            return
        total_stocks = 0
        for _, row in df.iterrows():
            symbol = row['Symbol'].replace('.','-')
            name = row['Security']
            
            
            stock, created = Stock.objects.get_or_create(symbol=symbol,defaults={'name':name})
            if created:
                total_stocks += 1

            print(f'getting data for {symbol}')

            try:
                df = yf.download(symbol, period='30d', interval='1d',progress=False)
                for date,row in df.iterrows():
                    PriceHistory.objects.update_or_create(
                        stock=stock,
                        date=date.date(),
                        defaults={'price': row['Close']}
                    )
            except Exception as e:
                print(f'Error for {symbol}:{e}')
        print('finish')