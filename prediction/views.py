from django.http.response import HttpResponse
from django.shortcuts import render
import redis
import json

# Create your views here.

def index(request):
    if (request.user.is_authenticated):
        #return HttpResponse("ok")
        if request.method == "GET" and request.GET['name'] != '':
            context = {}
            r = redis.StrictRedis(host='localhost',port='6379',db=0,password='Stock@123')
            name = request.GET['name']
            i = name + '_pred'
            res = json.loads(r.get(i))   #Retriving data from json         
            context['G1'] = res[0]['fig2'] #(fig2.to_html())    
            context['G2'] = res[0]['fig']  #(fig.to_html())
            res2 = json.loads(r.get(name+"pred_arima"))

            context['G3'] = res2[0]['fig3']
            context['Name'] = name
            return render(request,'pred.html',context)
        else:
            return HttpResponse("<h1> ERROR in page <a href=\'/dashboard\'> Go back </a> </h1>")
    else:
        return HttpResponse("<h1> ERROR in page <a href=\'/dashboard\'> Go back </a> </h1>")
