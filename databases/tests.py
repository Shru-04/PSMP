import random
import string
from django.test import TestCase
import yfinance as yf
import pandas as pd
from databases.models import *

# Create your tests here.

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

class Stock_and_CompanyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        x = pd.read_csv(r'C:\Users\SHRUJAN-R\Desktop\EQUITY_L.csv')
        y = x['SYMBOL'].tolist()[100:105]
        li = []
        for i in y:
            li.append(i + '.NS')
        li = ['AXISBANK.NS','BHARTIARTL.NS','CIPLA.NS','HCLTECH.NS','ICICIBANK.NS','ITC.NS','KOTAKBANK.NS','JSWSTEEL.NS','MARUTI.NS','POWERGRID.NS','SBIN.NS','TATAMOTORS.NS','TATASTEEL.NS','TCS.NS','WIPRO.NS','EICHERMOT.NS','GRASIM.NS', 'HINDUNILVR.NS', 'LT.NS', 'NESTLEIND.NS', 'NTPC.NS','SUNPHARMA.NS', 'TECHM.NS']
        for stocks in li:
            try:
                stk_res,cmp_res = get_stock_data(stocks)
                st = Stock()
                co = Company()
                st.Name = str(stk_res['Name'])
                print(st.Name)
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
                co.clean()
                co.save()
            except (TypeError):
                continue
        
    def test_ISIN(self):
        stks = Stock.objects.all()
        for i in stks:
            s = i.ISIN
            self.assertNotEqual(i.ISIN,'-',f"No ISIN for {i.Name}")

class Investor_and_BankTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        for i in range(100):
            inv = Investor()
            un = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=1000000))
            pa = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randrange(4,100)))
            fn = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randrange(4,100)))
            ln = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randrange(4,100)))
            em = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randrange(4,100))) + '@' + 'gmail.com'
            cn = ''.join(random.choices(string.digits,k=13))
            pcn = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randrange(4,100)))
            st = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randrange(4,100)))
            ci = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randrange(4,100)))
            dis = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randrange(4,100)))
            pc = random.randint(0,1e8)

            inv.Username = un
            inv.Password = pa
            inv.First_Name = fn
            inv.Last_Name = ln
            inv.Email_id = em
            inv.Contact_no = cn
            inv.Pan_card_no = pcn
            inv.State = st
            inv.District = dis
            inv.city = ci
            inv.Pin_code = pc

            inv.clean_fields()
            inv.save()

            bnk = Bank()
            bnk.Account_no = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randint(4,1000)))
            bnk.Username = inv
            bnk.IFSC_code = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randint(4,1000)))
            bnk.Branch = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,k=random.randint(4,1000)))

            bnk.clean()
            bnk.save()
            print(bnk.Username)
            """
            sss
             Username = models.CharField(max_length=1000,primary_key=True,unique=True)
    Password = models.CharField(max_length=1000,unique=True)
    First_Name = models.CharField(max_length=1000,unique=True)
    Last_Name = models.CharField(max_length=1000)
    Email_id = models.CharField(max_length=1000,validators=[validate_email],unique=True)
    Contact_no = models.CharField(max_length=13,unique=True)
    Pan_card_no = models.CharField(max_length=1000,unique=True)
    Address_Line = models.CharField(max_length=5000,default='empty')
    State = models.CharField(max_length=1000)
    city = models.CharField(max_length=1000)
    District = models.CharField(max_length=1000)
    Pin_code = models.IntegerField()
            """

    def test_Uniqueness(self):
        inv = Investor.objects.all()
        dictionary = {}
        for i in inv:
            dictionary[i] = 0
        for i in inv:
            dictionary[i] = dictionary[i] + 1
        for i in inv:
            self.assertEqual(dictionary[i],1,f"{i.Username}")

            

"""
So, after testing
Do these changee:
1. Change databases.Bank.Username: to OneToOneField
2. Validate all objects before saving, by using obj.clean_fields() rather than just obj.clean()
3. Stock API is fluctuating, so either ignore stocks having isin '-' or delete them
"""
