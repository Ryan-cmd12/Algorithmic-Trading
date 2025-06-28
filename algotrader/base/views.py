from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponse
from .models import Portfolio, PriceHistory, Stock, Trade
from datetime import date
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.db.models import Case, Value, When, OuterRef, Subquery
from django.contrib import messages
from .utils import g_holdings
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth import logout as auth_logout
from .forms import Register_form
from django.db.models import Q
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from io import BytesIO

# Create your views here.


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist, please try again')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username or password is incorrect, please try again')
    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def Register(request):
    form = Register_form()
    if request.method == 'POST':
        form = Register_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            messages.error(request, 'Error has occurred')
    context = {'form':form}
    return render(request, 'base/login_register.html', context)



def logoutUser(request):
    #deletes session
    logout(request)
    return redirect('dashboard')


@login_required(login_url='login')
def dashboard(request):
    portfolio = get_object_or_404(Portfolio, user=request.user)
    trades = Trade.objects.filter(portfolio=portfolio)
    trades_dashboard = trades.order_by('-date')[:10]
    #.values(symbolstock)creates a dictionary {'symbol_stock':Stock.name}
    #annotate adds (total_qty into dict)
    #Case(When(condition, then=)) if when is true then ...
    #output field to let django know what they are getting(integerfield)
    #__gt=0 keep if total_quantity >0 (still have shares)

    # holdings = (trades.values('symbol__stock').annotate(total_quantity=Sum(F('quantity')* 
    #                                                                       Case(When(trade_type='SELL', then=-1),
    #                                                                            When(trade_type='BUY', then=1),
    #                                                                            output_field=models.IntegerField)
    #                                                                       ))).filter(total_quantity__gt=0)
    net_worth = g_portfolio_value(portfolio)
    context = {'Portfolio':portfolio,'trades_dashboard':trades_dashboard, 'net_worth': net_worth }
    return render(request, 'base/dashboard.html', context)

@login_required
def stock_list(request):
    query = request.GET.get('q', '').strip()
    #Outeref is used inside the subquery to ref outer queries current row uisng pk
    latest_price_subquery = PriceHistory.objects.filter(stock=OuterRef('pk')).order_by('-date')
    stocks = Stock.objects.all()
    if query:
        stocks = stocks.filter(
            Q(symbol__icontains=query) |
            Q(name__icontains=query)
        )
    # stock_data = []
    # for stock in stocks:
    #     latest_price = PriceHistory.objects.filter(stock=stock).order_by('-date').first()
    #     stock_data.append({
    #         'stock':stock,
    #         'latest_price':latest_price if latest_price else 'data not available'
    #     })
    #subquery searches each row in the outeref [:1] to find latest price n date
    stocks = stocks.annotate(
        latest_price=Subquery(latest_price_subquery.values('price')[:1]),
        latest_price_date=Subquery(latest_price_subquery.values('date')[:1])
    )
    context = {'stocks': stocks, 'query':query}
    return render(request, 'base/stock_list.html', context)


def stock_graph_view(request):
    symbol = request.GET.get('symbol')
    stock = Stock.objects.get(symbol=symbol)
    latest_price_subquery = PriceHistory.objects.filter(stock=OuterRef('pk')).order_by('-date')
    curr_day = Subquery(latest_price_subquery.values('date')[:1])
    start_day = curr_day - timedelta(days=30)
    price_data= PriceHistory.objects.filter(stock=stock, date__gte=start_day).order_by('date')
    dates = []
    prices = []
    for record in price_data:
        dates.append(record.date)
        prices.append(record.price)

    plt.figure(figsize=(8, 5))
    plt.plot(dates, prices, marker='o')
    plt.title(f"{stock.symbol} - Last 30 Days Price")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.grid(True)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Return image as response
    return HttpResponse(buf.getvalue(), content_type='image/png')


@login_required
def Trader(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    portfolio= get_object_or_404(Portfolio,user=request.user)
    owned_stocks = g_holdings(stock) if g_holdings(stock) else 0

    latest_price_obj = PriceHistory.objects.filter(stock=stock)
    latest_price = latest_price_obj.price if latest_price_obj else None
    
    if request.method == 'POST':
        trade_type = request.POST['trade_type']
        quantity = request.POST['quantity']

        cost = quantity * latest_price
        if trade_type == 'BUY':
            if portfolio.cash >=cost:
                portfolio.cash -= cost
                portfolio.save()
                Trade.objects.create(portfolio=portfolio,stock=stock,quantity=quantity,price=latest_price, trade_type='BUY')
                messages.success(request, f'Bought {quantity} shares of {stock} successfully')
            else:
                messages.error(request, 'Insufficient funds')
        elif trade_type=='SELL':
            if quantity <= owned_stocks:
                portfolio.cash += cost
                portfolio.save()
                Trade.objects.filter(portfolio=portfolio, stock=stock,quantity=quantity,price=latest_price, trade_type='BUY')
            messages.success(request, f'Sold {quantity} shares of {stock} successfully')
        
    context= {'stock':stock, 'portfolio': portfolio, 'owned_stocks':owned_stocks}
    return render(request, 'base/trading.html', context)

def g_portfolio_value(portfolio):
    holdings = g_holdings(portfolio)
    value = portfolio.cash
    for stock,qty in holdings.items():
        latest_price = int(PriceHistory.objects.filter(stock=stock).order_by('-date').first())
        if latest_price:
            value += qty * latest_price
    return round(value,2)

