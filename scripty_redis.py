# Link : https://www.geeksforgeeks.org/running-python-program-in-the-background/
# Link : https://pypi.org/project/schedule/

import schedule
import yfinance as yf
import redis
import time
from datetime import date, datetime
import json



def get_topnews(ticker_obj,p):
    result = []
    news_data = ticker_obj.news[:p]
    for item in news_data:
        result.append({key: item[key] for key in item.keys() & {'title','link'}})
    return result


def redis_data():
    # Link : https://stackoverflow.com/questions/15219858/how-to-store-a-complex-object-in-redis-using-redis-py
    r = redis.StrictRedis(host='localhost',port='6379',db=0,password='Stock@123')
    p = 5
    stock_name =  ['AXISBANK.NS','BHARTIARTL.NS','CIPLA.NS','HCLTECH.NS','ICICIBANK.NS','ITC.NS','KOTAKBANK.NS','JSWSTEEL.NS','MARUTI.NS','POWERGRID.NS','SBIN.NS','TATAMOTORS.NS','TATASTEEL.NS','TCS.NS','WIPRO.NS','EICHERMOT.NS','GRASIM.NS', 'HINDUNILVR.NS', 'IOC.NS', 'LT.NS', 'NESTLEIND.NS', 'NTPC.NS','SUNPHARMA.NS', 'TECHM.NS', 'ULTRACEMCO.NS']
    for i in stock_name:
        data=yf.Ticker(i)
        res = get_topnews(data,p)
        print(res)
        x = json.dumps(res)
        r.set(i,x)
        r.save()
    print("Done")

schedule.every(3).minutes.do(redis_data)

while(True):
    schedule.run_pending()
    time.sleep(1)