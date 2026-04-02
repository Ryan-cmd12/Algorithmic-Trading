from django.core.management.base import BaseCommand
from base.models import FuturesContract, FuturesPriceHistory
import pandas as pd
import re
import requests
import yfinance as yf

CODE_TO_MNTH = {
    "F": 1,   # Jan
    "G": 2,   # Febr
    "H": 3,   # Mar
    "J": 4,   # Apr
    "K": 5,   # May
    "M": 6,   # Jun
    "N": 7,   # Jul
    "Q": 8,   # Aug
    "U": 9,   # Sept
    "V": 10,  # Oct
    "X": 11,  # Nov
    "Z": 12,  # Dec
}

MNTH_IN_ORDER = {"F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"}

def parse_futures_symbol(symbol):
    match = re.match(r"([A-Z]+)([FGHJKMNQUVXZ])(\d{2})", symbol)
    if not match:
        raise ValueError(f"Invalid futures symbol format: {symbol}")
    
    root_symbol, month_code, year_suffix = match.groups()
    month = CODE_TO_MNTH.get(month_code)
    if month is None:
        raise ValueError(f"Invalid month code in symbol: {month_code}")
    
    year = 2000 + int(year_suffix)  # Assuming 21st century
    return root_symbol, month, year

#generates a list of constracts in order 
def generate_contract_list(root_symbol : str, start: int, end: int):
    contracts = []

    for year in range(start, end + 1):
        year_suffix = str(year)[-2:]
        for mnth in MNTH_IN_ORDER:
            symbol = f"{root_symbol.upper()}{mnth}{year_suffix}"
            contracts.append(symbol)
    return contracts

def yahoo_converter(symbol: str):
    root, mnth, year = parse_futures_symbol(symbol)
    year_suffix = str(year)[-2:]
    yahoo_symbol = f"{root}=F{year_suffix}{mnth:02d}"
    return yahoo_symbol



class Command(BaseCommand):
    help = 'loads historical data for future contracts'

    def add_arguments(self, parser):
        #for those who want a specific contract 
        parser.add_argument(
            '--contract',
            type=str,
            help="Enter a specific future contract symbol (eg, ESZ23)" 
        )
        #for those who want to load a list of contracts for a root symbol and date range
        parser.add_argument(
            '--root',
            type=str,
            help="Enter root symbol to load all contracts for (eg, ES)"
        )
        parser.add_argument(
            '--start',
            type=int,
            help='Specify start year for contract list'
        )
        parser.add_argument(
            '--end',
            type=int,
            help='Specify end year for contract list'
        )
        parser.add_argument(
            '--period',
            type=str,
            default='1y',
            help='Specify historical period(eg, 1y, 6mo)'
        )
        parser.add_argument(
            '--interval',
            type=str,
            default='1d',
            help='Specify interval period'
        )
    def handle(self, *args, **options):
        contract = options.get('symbol')
        root = options.get('root')
        start = options.get('start')
        end = options.get('end')
        period = options.get('period')
        interval = options.get('interval')

        contracts = []
        if contract:
            contracts.append(contract.upper())
        elif root and start and end:
            contracts = generate_contract_list(root, start, end)
        else:
            print(f"Something went wrong!")
            return
        
        for contract in contracts:
            try:
                root_symbol, mnth, year = parse_futures_symbol(contract)
                print(f"Loading data for {contract} (Root: {root_symbol}, Month: {mnth}, Year: {year})")
            except ValueError as e: 
                print(f"Error parsing contract symbol {contract}: {e}")
                return
        futures_contract, created = FuturesContract.objects.get_or_create(symbol = contract, defaults={'root_symbol': root_symbol, 'month_code': mnth, 'year': year})
        if created:
            print(f"Created new futures contract: {contract} - Root: {root_symbol}, Month: {mnth}, Year: {year}")
        yahoo_symbol = yahoo_converter(contract)
        try:
            data = yf.download(yahoo_symbol, period=period, interval=interval, progress=False)
            