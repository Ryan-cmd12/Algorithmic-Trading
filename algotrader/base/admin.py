from django.contrib import admin
from .models import Stock, PriceHistory
# Register your models here.

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name')
    search_fields = ('symbol', 'name')

class PriceHistoryAdmin(admin.ModelAdmin):
    list_display=('stock', 'date', 'price')
    list_filter = ('stock', 'date')
    search_fields= ('stock__symbol',) #expects it to be tuple or list