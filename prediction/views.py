from django.http.response import HttpResponse
from django.shortcuts import render

import yfinance as yf
import datetime
import requests
import redis
import json
import plotly.graph_objs as go
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import keras
import tensorflow as tf
from keras.preprocessing.sequence import TimeseriesGenerator

from keras.models import Sequential
from keras.layers import LSTM, Dense

# Create your views here.
def predict(num_prediction, model,close_data,look_back):
    prediction_list = close_data[-look_back:]
    
    for _ in range(num_prediction):
        x = prediction_list[-look_back:]
        x = x.reshape((1, look_back, 1))
        out = model.predict(x)[0][0]
        prediction_list = np.append(prediction_list, out)
    prediction_list = prediction_list[look_back-1:]
        
    return prediction_list
    
def predict_dates(num_prediction,last_date):
    prediction_dates = pd.date_range(last_date, periods=num_prediction+1).tolist()
    return prediction_dates

def index(request):
    if (request.user.is_authenticated):
        #return HttpResponse("ok")
        if request.method == "GET" and request.GET['name'] != '':
    # else:
    #     return HttpResponse("<h1> Hello, ur not supposed to enter HERE !!!!! </h1>")

            # """
            # usage : 
            # (pred_graph,current_graph,predicted_values,predecited_dates) = predction("AAPL")
            # returns 10 days of predtion
            # """
            # name = request.GET['name']
            # data=yf.Ticker(name)
            # df = data.history(start='2020-01-01', end=datetime.datetime.today(), interval="1d")[["Open","High","Low","Close","Volume"]]
            # df.index = pd.to_datetime(df.index)
            # df.set_axis(df.index, inplace=True)
            # df.drop(columns=['Open', 'High', 'Low', 'Volume'], inplace=True)

            # close_data = df['Close'].values
            # close_data = close_data.reshape((-1,1))
            
            # close_train = close_data
            # date_train = df.index

            # look_back = 15

            # train_generator = TimeseriesGenerator(close_train, close_train, length=look_back, batch_size=20)

            # model = Sequential()
            # model.add(
            #     LSTM(20,
            #         activation='relu',
            #         input_shape=(look_back,1))  
            # )
            # model.add(Dense(1))
            # model.compile(optimizer='adam', loss='mse')

            # num_epochs = 30
            # model.fit_generator(train_generator, epochs=num_epochs, verbose=1)

            # close_data = close_data.reshape((-1))


            # num_prediction = 10
            # forecast = predict(num_prediction, model,close_data,look_back)
            # forecast_dates = predict_dates(num_prediction,df.index.values[-1])



            # new_array = np.array(df.index.to_pydatetime())

            # new_array = [x.strftime('%y-%m-%d') for x in new_array]

            # curr_val = close_data[-1]
            # diff = curr_val - forecast[0]
            # forecast = forecast + diff

            
            # trace1 = go.Scatter(
            #     x=df.index[-150:], y=close_data[-150:],
            #     mode = 'lines',
            #     name = 'Data'
            # )
            # trace2 = go.Scatter(
            #     x=forecast_dates,y= forecast,
            #     mode = 'lines',
            #     name = 'Prediction'
            # )
            # layout = go.Layout(
            #     title = name + " Predicted Values",
            #     xaxis = {'title' : "Date"},
            #     yaxis = {'title' : "Close"}
            # )

            # tracefig2 = go.Scatter(
            #     x=new_array,y= close_data
            # )
            # layoutfig2 = go.Layout(
            #     title = name,
            #     xaxis = {'title' : "Date"},
            #     yaxis = {'title' : "Close"}
            # )
            # fig2 = go.Figure(data=[tracefig2], layout=layoutfig2)
            # fig = go.Figure(data=[trace1, trace2], layout=layout)
            context = {}
            r = redis.StrictRedis(host='localhost',port='6379',db=0,password='Stock@123')
            name = request.GET['name']
            i = name + '_pred'
            res = json.loads(r.get(i))   #Retriving data from json          #print(json.loads(r.get(i))[0]['fig'])
            context['G1'] = res[0]['fig2'] #(fig2.to_html())    
            context['G2'] = res[0]['fig']  #(fig.to_html())
            res2 = json.loads(r.get(name+"pred_arima"))

            context['G3'] = res2[0]['fig3']
            context['Name'] = name
            return render(request,'pred.html',context)
            #return (fig2.to_html(),fig.to_html(),forecast,forecast_dates)
            #return (fig2,fig,forecast,forecast_dates)
        else:
            return HttpResponse("<h1> ERROR in page <a href='dashboard:index'> Go back </a> </h1>")
    else:
        return HttpResponse("<h1> ERROR in page <a href='dashboard:index'> Go back </a> </h1>")
