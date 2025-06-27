from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
class PriceHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_history')
    date = models.DateField()
    price = models.FloatField()

    class Meta:
        #unique tgr ensures no duplicate sets
        unique_together = ('stock', 'date')
        ordering = ['date']
    
    def __str__(self):
        return f"{self.stock.symbol} was ${self.price:.2f} on {self.date}"
    
class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash = models.FloatField(default=100000.0)
    start_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s portfolio - Cash: ${self.cash:.2f}, created on {self.start_date}"
    
class Trade(models.Model):
    Trade_types =[
        ('BUY', 'Buy'),
        ('SELL', 'sell')
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='trades')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField()
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    trade_type = models.CharField(max_length=4, choices= Trade_types)
    
    @property #property so u can call self.total_price instead of total_price()
    def total_price(self):
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.trade_type}{self.quantity} of {self.stock} at ${self.price:.2f} on {self.date.date()}, Total = ${self.total_price:.2f}"

