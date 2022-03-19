from datetime import date, datetime
import json
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.http import HttpResponse
import yfinance as yf
from databases.models import Bank, Company, Investment, Stock, Investor
import plotly.graph_objs as go
from django.contrib.auth.models import User
import redis

# Create your views here.

def index(request):
    return HttpResponse("OK")

def stock_manage(request):
    if request.user.is_authenticated :
        #define the ticker symbol
        print(request.GET)
        stockt = request.GET['name'] #'TATAPOWER.NS'
        #get data on this ticker
        data = yf.Ticker(stockt).history(start='2021-01-02',end=datetime.today().strftime('%Y-%m-%d'),interval="1d")[["Open","High","Low","Close","Volume"]]
        stockdata = data.info
        #stock = Stock(request.POST)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index,open = data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name = 'market data'))
        fig.update_layout(title = f'share price of {stockt}', yaxis_title = 'Stock Price')
        x = fig.to_html()
        context = {}
        context['stock'] = x
        return HttpResponse(x)
    else:
        return HttpResponse("<h1> Illegal request </h1>")

def user_stock(request):
    if request.user.is_authenticated:
        if Stock.objects.filter(ISIN = Investment.objects.get(User_Account_no= Bank.objects.get(Username=request.user.username).Account_no).Stock_ISIN).exists() is True:
            stocku = Stock.objects.get(ISIN = Investment.objects.get(User_Account_no= Bank.objects.get(Username=request.user.username).Account_no).Stock_ISIN)
            return HttpResponse("ok<br>{{stocku}}")
        else:
            return HttpResponse("Error")
        

def redis_data(request):
    # Link : https://stackoverflow.com/questions/15219858/how-to-store-a-complex-object-in-redis-using-redis-py
    r = redis.StrictRedis(host='redis',port='6379',db=0,password='Stock@123')
    if request.user.is_authenticated:
        if request.method == 'GET':
            name = request.GET['name']
            data=yf.Ticker(name)     
            res = json.loads(r.get(name))

            context={}
            context['news'] = res
            context['name'] = name
            stockobj = Stock.objects.get(Name=name)
            #print(stockobj)
            context['stock'] = stockobj
            uname = request.user.username
            bankobj=Bank.objects.get(Username=uname)
            accno=bankobj.Account_no
            bought = Investment.objects.raw("SELECT * from databases_investment WHERE User_Account_no_id='"+accno+"' AND Stock_ISIN_id = '"+str(stockobj.ISIN)+"'")
           
            
            bought_stk = Investment.objects.raw("SELECT id,SUM(Quantity) as totalstk,SUM(Quantity*Purchased_value) AS usersum,SUM(Quantity*Current_price) as stksum from databases_investment LEFT JOIN databases_stock ON databases_investment.Stock_ISIN_id=databases_stock.ISIN WHERE databases_stock.ISIN='"+str(stockobj.ISIN)+"' AND  User_Account_no_id='"+accno+"'")
            #added below
            XY = Investment.objects.raw("SELECT id,SUM(Quantity) as X from databases_investment where User_Account_no_id='"+accno+"' AND Stock_ISIN_id = '"+str(stockobj.ISIN)+"'"+" AND Transaction_Mode = 'Buy'")
            YZ = Investment.objects.raw("SELECT id,SUM(Quantity) as X from databases_investment where User_Account_no_id='"+accno+"' AND Stock_ISIN_id = '"+str(stockobj.ISIN)+"'"+" AND Transaction_Mode = 'Sell'")
            for i in XY:
                print (i.X)
            for i in YZ:
                print (i.X)
            context['invests'] = {}
            
            for x in bought_stk:
                if x.totalstk is not None:
                    context['invests']['totalstk'] = int(x.totalstk)
                else : 
                    context['invests']['totalstk'] = 0
                context['invests']['usersum'] = x.usersum
                context['invests']['stksum'] = x.stksum
            context['bought']=bought
            cmpy = Company.objects.get(Stock_ISIN=stockobj)
            context['cmpy'] = cmpy
            
            return render(request,'apinews.html',context)
        else:
            return HttpResponse("<h1> Hello, ur not supposed to enter HERE !!!!! </h1>")
    else:
        return HttpResponse("<h1> Hello, ur not supposed to enter HERE !!!!! </h1>")



def buyupdate(request):
    print(request.POST)
    if request.user.is_authenticated and 'Buy' in request.POST:
        print(request.POST)
        if request.POST['Quantity'] == '':
            messages.error(request,"Please Enter quantity")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
        quantity = int(request.POST['Quantity']) # GET from page
        stk_name = request.GET['name']#"TATAPOWER.NS" #GET FROM PAGE
        loguser = request.user.username
        bankobj=Bank.objects.get(Username=loguser)
        accno=bankobj.Account_no
        stk = Stock.objects.get(Name=stk_name)
      
        done = 0
        vals = {"curr" : bankobj.Current_amount 
        }

        if(bankobj.Current_amount < stk.Current_price*quantity):
            messages.error(request,"Buy fail, You dont have Enough Amount in your account")
            return redirect('/db/apidata'+'?name='+request.GET['name'])

        stk = Stock.objects.get(Name=stk_name)
        investobj = Investment()
        investobj.Quantity = quantity
        investobj.Date_of_Purchased = datetime.today()
        investobj.Purchased_Value = stk.Current_price
        investobj.User_Account_no = bankobj
        investobj.Stock_ISIN = stk
        investobj.Transaction = 'Buy'   #add
        investobj.save()
        bankobj.Current_amount -= int(stk.Current_price*int(quantity))
        bankobj.save()
        
        done = 1
        if(done==0) :
            messages.error(request,"Buy fail")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
        else:
            messages.success(request,f'Hurray !!! Stock {stk_name} Brought @ Rs. {int(stk.Current_price*int(quantity))}')
            return redirect('dashboard:index')
    elif request.user.is_authenticated and 'Sell' in request.POST:
        return sellupdate(request) #redirect('databases:sell')#
    else:
        return HttpResponse("<h1> Buy fail <a href = \'/dashboard\'> go back </a></h1>")


def sellupdate(request):
    if request.user.is_authenticated and 'Sell' in request.POST:
        print(request.POST)
        if request.POST['Quantity'] == '':
            messages.error(request,"Please Enter quantity")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
        quantity = int(request.POST['Quantity']) # GET from page
        stk_name = request.GET['name'] #"TATAPOWER.NS" #GET FROM PAGE
        loguser = request.user.username
        bankobj = Bank.objects.get(Username=loguser)
        accno=bankobj.Account_no
        invested = Investment.objects.raw("SELECT id,Stock_ISIN_id FROM databases_investment WHERE User_Account_no_id='"+accno+"'")
        stk = Stock.objects.get(Name = stk_name)
        bought = Investment.objects.raw("SELECT * from databases_investment WHERE User_Account_no_id='"+accno+"' AND Stock_ISIN_id = '"+str(stk.ISIN)+"'")
        total = Investment.objects.filter(Stock_ISIN= stk.ISIN,User_Account_no=accno).aggregate(Sum('Quantity'))
        total = total['Quantity__sum']

        print(total)
        if( quantity is None or total is None) : 
            messages.error(request,"Error !! Not enough quantity in your holdings")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
        if( quantity > total) : 
            messages.error(request,"Error !! Not enough quantity in your holdings")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
        
        stkcurr = stk.Current_price
        x = Investment()
        x.Quantity = -quantity
        x.Date_of_Purchased = datetime.today()
        x.Purchased_Value = stkcurr
        x.User_Account_no = bankobj
        x.Stock_ISIN = stk
        x.Transaction_Mode = 'Sell'   #add
        x.save()
        bankobj.Current_amount += stkcurr * abs(x.Quantity)
        bankobj.save()

        if(bought is None) :
            messages.error(request,"Error !! you have not purchased stock")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
            return HttpResponse('<h1> you have not purchased stock <a href = \'databases:apidata\'> go back </a></h1>') #say you have not purchased stock
        else:
            messages.success(request,f"U sold {stk_name} @ Rs. {stkcurr} for {quantity} no.s")
            return redirect('dashboard:index')
    elif request.user.is_authenticated and 'Buy' in request.POST:
        return buyupdate(request) # redirect('databases:buy_sell')  #
    else:
        return HttpResponse("<h1> Sell fail <a href = \'/dashboard\'> go back </a></h1>")


