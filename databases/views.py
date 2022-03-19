from datetime import date, datetime
import json
from django.contrib import messages
import re
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.http import HttpResponse
import yfinance as yf
import numpy as np
from databases.models import Bank, Company, Investment, Stock, Investor
import plotly.graph_objs as go
from django.contrib.auth.models import User
import redis

# Create your views here.

import pytz

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
        #print(x,"123")
        return HttpResponse(x)
    else:
        return HttpResponse("<h1> Illegal request </h1>")
    # return render(request,'index.html',context)

def user_stock(request):
    if request.user.is_authenticated:
        if Stock.objects.filter(ISIN = Investment.objects.get(User_Account_no= Bank.objects.get(Username=request.user.username).Account_no).Stock_ISIN).exists() is True:
            stocku = Stock.objects.get(ISIN = Investment.objects.get(User_Account_no= Bank.objects.get(Username=request.user.username).Account_no).Stock_ISIN)
            return HttpResponse("ok<br>{{stocku}}")
        else:
            return HttpResponse("Error")
        
def get_stock_data(stock_name):
    data=yf.Ticker(stock_name)
    info = data.info
    stk_values = {'currentPrice','beta','volume','regularMarketOpen','revenueGrowth','dayHigh','open','previousClose','dayLow'}
    cmp_values = {'sector','industry','longBusinessSummary','website','grossProfits','longName'}
    stk_res = {key: info[key] for key in info.keys() & stk_values}
    cmp_res = {key: info[key] for key in info.keys() & cmp_values}
    stk_res['ISIN'] = data.isin
    stk_res['Name'] = stock_name
    cmp_res['ISIN'] = stk_res['ISIN']
    return stk_res,cmp_res

def fill_db(request):
    if request.user.is_superuser:
        #st = Stock()
        #stk_list = ['AXISBANK.NS','BHARTIARTL.NS','CIPLA.NS','HCLTECH.NS','ICICIBANK.NS','ITC.NS','KOTAKBANK.NS','JSWSTEEL.NS','MARUTI.NS','POWERGRID.NS','SBIN.NS','TATAMOTORS.NS','TATASTEEL.NS','TCS.NS','WIPRO.NS','EICHERMOT.NS','GRASIM.NS', 'HINDUNILVR.NS', 'IOC.NS', 'LT.NS', 'NESTLEIND.NS', 'NTPC.NS','SUNPHARMA.NS', 'TECHM.NS', 'ULTRACEMCO.NS']
        entries= Stock.objects.all()
        return HttpResponse(f"ok<br>{{Stock.objects.all}}")
    else:
        return HttpResponse("<h1> Hello, ur not supposed to enter HERE !!!!! </h1>")


def fill_db2(request):
    if request.user.is_superuser:
        stk_list = ['AXISBANK.NS','BHARTIARTL.NS','CIPLA.NS','HCLTECH.NS','ICICIBANK.NS','ITC.NS','KOTAKBANK.NS','JSWSTEEL.NS','MARUTI.NS','POWERGRID.NS','SBIN.NS','TATAMOTORS.NS','TATASTEEL.NS','TCS.NS','WIPRO.NS','EICHERMOT.NS','GRASIM.NS', 'HINDUNILVR.NS', 'IOC.NS', 'LT.NS', 'NESTLEIND.NS', 'NTPC.NS','SUNPHARMA.NS', 'TECHM.NS', 'ULTRACEMCO.NS']
        for x in stk_list:
            stk_res,cmp_res = get_stock_data(x)
            if (Stock.objects.filter(ISIN = str(stk_res['ISIN'])).exists() is False):
                st = Stock() 
                co = Company()
            else:
                st = Stock.objects.get(ISIN = str(stk_res['ISIN']))
                co = Company.objects.get(Stock_ISIN=str(cmp_res['ISIN']))
            st.Name = str(stk_res['Name'])
            st.ISIN = str(stk_res['ISIN'])
            st.Volume = int(stk_res['volume'])
            st.Prev_Close = float(stk_res['previousClose'])
            st.Day_low =  float(stk_res['dayLow'])
            st.Current_price =  float(stk_res['currentPrice'])
            st.Beta =  float(stk_res['beta'])
            st.Regular_market_open =  float(stk_res['regularMarketOpen'])
            st.Day_high =  float(stk_res['dayHigh'])
            st.Open =  float(stk_res['open'])
            st.Revenue_growth =  float(stk_res['revenueGrowth'])

            st.clean()
            st.save()
            
            co.Name = str(cmp_res['longName'])
            co.Stock_ISIN = Stock.objects.get(ISIN=str(cmp_res['ISIN']))
            co.Sector = str(cmp_res['sector'])    
            co.Industry = str(cmp_res['industry'])
            co.Business_Summary =str(cmp_res['longBusinessSummary'])
            co.Website = cmp_res['website']
            co.Gross_Profit = float(cmp_res['grossProfits'])

            print(st,co)
            co.clean()
            co.save()
        x = Stock.objects.all()
        return HttpResponse("ok<br>{{x}}")
    else:
        return HttpResponse("<h1> Hello, ur not supposed to enter HERE !!!!! </h1>")


def get_topnews(ticker_obj,p):
    result = []
    news_data = ticker_obj.news[:p]
    for item in news_data:
        result.append({key: item[key] for key in item.keys() & {'title','link'}})
    return result

def redis_data(request):
    # Link : https://stackoverflow.com/questions/15219858/how-to-store-a-complex-object-in-redis-using-redis-py
    r = redis.StrictRedis(host='localhost',port='6379',db=0,password='Stock@123')
    # if request.user.is_superuser:
    #     if (request.GET['num'] == ''):
    #         return HttpResponse("<h1> Hello, ur not supposed to enter HERE !!!!! </h1>")
    #     p = int(request.GET['num'])
    #     stock_name =  ['AXISBANK.NS','BHARTIARTL.NS','CIPLA.NS','HCLTECH.NS','ICICIBANK.NS','ITC.NS','KOTAKBANK.NS','JSWSTEEL.NS','MARUTI.NS','POWERGRID.NS','SBIN.NS','TATAMOTORS.NS','TATASTEEL.NS','TCS.NS','WIPRO.NS','EICHERMOT.NS','GRASIM.NS', 'HINDUNILVR.NS', 'IOC.NS', 'LT.NS', 'NESTLEIND.NS', 'NTPC.NS','SUNPHARMA.NS', 'TECHM.NS', 'ULTRACEMCO.NS']
    #     for i in stock_name:
    #         if r.get(i) is None or p != 0:
    #             data=yf.Ticker(i)
    #             res = get_topnews(data,p)
    #             print(res)
    #             x = json.dumps(res)
    #             r.set(i,x)
    #             r.save()
    #     res = json.loads(r.get(stock_name[0]))  #Retriving data from json
    #     y = res[0]['title']
    #     return HttpResponse(f'<h1> okk <br><br>{y} </h1>')
    if request.user.is_authenticated:
        if request.method == 'GET':
            name = request.GET['name']
            data=yf.Ticker(name)     
            #res2 = json.dumps(get_topnews(data,5))
            res = json.loads(r.get(name))
            # if str(res2) != str(res):
            #     r.set(name,res2)
            #     r.save()
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
            # print(XY.X)  added above
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
            
           # context['cmpy']['Gross_Profit'] =  numerize.numerize(context['cmpy']['Gross_Profit'] )
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
            #return HttpResponse('<h1>Please Enter quantity <a href = \'/dashboard\'> go back </a></h1>')
        quantity = int(request.POST['Quantity']) # GET from page
        stk_name = request.GET['name']#"TATAPOWER.NS" #GET FROM PAGE
        loguser = request.user.username
        bankobj=Bank.objects.get(Username=loguser)
        #investor = Investor.objects.get(Username = loguser)         #add
        accno=bankobj.Account_no
        stk = Stock.objects.get(Name=stk_name)
        # curr_amount = accno.Current_amount
        # invested = Investment.objects.raw("SELECT id,Stock_ISIN_id FROM databases_investment WHERE User_Account_no_id='"+accno+"'")
        # purchased = 0
        done = 0
        vals = {"curr" : bankobj.Current_amount 
        }
        # bought = Investment.objects.raw("SELECT * from databases_investment WHERE User_Account_no_id='"+accno+"' AND Stock_ISIN_id = '"+str(stockobj.ISIN)+"'")
        if(bankobj.Current_amount < stk.Current_price*quantity):
            messages.error(request,"Buy fail, You dont have Enough Amount in your account")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
            #return HttpResponse("<h1> Buy fail, You dont have Enough Amount in your account <a href = \'/dashboard\'> go back </a> </h1>")
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
        #investor.Stocks_Purchased += quantity   #add
        #investor.save()                         #add
        done = 1
        if(done==0) :
            messages.error(request,"Buy fail")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
            #return HttpResponse("<h1> Buy fail </h1>")
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
            #return HttpResponse('<h1>Please Enter quantity <a href = \'/dashboard\'> go back </a> </h1>')
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
            #return HttpResponse('<h1> Not enough quantity in your holdings <a href = \'/dashboard\'> go back </a></h1>')
        if( quantity > total) : 
            messages.error(request,"Error !! Not enough quantity in your holdings")
            return redirect('/db/apidata'+'?name='+request.GET['name'])
            #return HttpResponse('<h1> Not enough quantity in your holdings <a href = \'/dashboard\'> go back </a></h1>')
        
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
        ###
        '''
        total = quantity
        stkcurr = stk.Current_price
        for x in bought : 
            if(total ==0) : break
            if(x.Quantity < total) :
                total-=x.Quantity
                bankobj.Current_amount += stkcurr * x.Quantity
                x.delete()
            else :
                x.Quantity-=total
                bankobj.Current_amount += stkcurr * total
                total = 0
                if(x.Quantity == 0) : x.delete()
                else : x.save()
            bankobj.save()
                
        '''
        ### 

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


