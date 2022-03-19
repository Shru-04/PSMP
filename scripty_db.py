##Link : https://stackoverflow.com/questions/8047204/python-script-for-django-app-to-access-models-without-using-manage-py-shell

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockplatform.settings")
import django
django.setup()

from databases.models import Bank, Company, Investment, Stock, Investor
from datetime import date, datetime
import json
import yfinance as yf
import schedule
import time

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

def fill_db2():
    stk_list = ['AXISBANK.NS','BHARTIARTL.NS','CIPLA.NS','HCLTECH.NS','ICICIBANK.NS','ITC.NS','KOTAKBANK.NS','JSWSTEEL.NS','MARUTI.NS','POWERGRID.NS','SBIN.NS','TATAMOTORS.NS','TATASTEEL.NS','TCS.NS','WIPRO.NS','EICHERMOT.NS','GRASIM.NS', 'HINDUNILVR.NS', 'IOC.NS', 'LT.NS', 'NESTLEIND.NS', 'NTPC.NS','SUNPHARMA.NS', 'TECHM.NS']
    for x in stk_list:
        stk_res,cmp_res = get_stock_data(x)
        if (stk_res['ISIN'] == '-'):
            continue
        if (Stock.objects.filter(ISIN = str(stk_res['ISIN'])).exists() is False):
            st = Stock() 
            co = Company()
            if (Stock.objects.filter(Name=str(stk_res['Name'])).exists() is True):
                st = Stock.objects.get(Name = str(stk_res['Name']))
                co = Stock.objects.get(Stock_ISIN=str(st.ISIN))
                if (Investment.objects.filter(Stock_ISIN=str(st.ISIN)).exists() is True):
                    ins = Investment.objects.get(Stock_ISIN=str(st.ISIN))
                    ins.Stock_ISIN = str(stk_res['ISIN'])
                    ins.save()
                #if (Investment.ob)
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

# schedule.every(1).minutes.do(fill_db2)

# while(True):
#     schedule.run_pending()
#     time.sleep(1)

fill_db2()