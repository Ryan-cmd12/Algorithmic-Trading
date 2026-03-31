from django.core.management.base import BaseCommand
from base.models import Stock, PriceHistory
import pandas as pd


class Command(BaseCommand):
    help = 'loads historical data for future contracts'