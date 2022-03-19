from django.core.checks.messages import INFO
from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from databases.models import *
# Create your views here.
def index(request):
    if (request.user.is_authenticated):
        stockobj = Stock.objects.raw("SELECT * FROM databases_stock ORDER BY beta DESC")
        name = request.user.username
        investordetails = Investor.objects.get(Username=name)
        
        bankobj=Bank.objects.get(Username=name)
        accno=bankobj.Account_no
        invested = Investment.objects.raw("SELECT id,Stock_ISIN_id,SUM(Quantity) as sum_quan,SUM(Purchased_Value*Quantity) AS VALUE FROM databases_investment WHERE User_Account_no_id='"+accno+"'" + "GROUP BY Stock_ISIN_id")
        investedtotal = Investment.objects.raw("SELECT id,Stock_ISIN_id FROM databases_investment WHERE User_Account_no_id='"+accno+"'" )

        recommned = Stock.objects.raw("Select ISIN,Name from databases_stock ORDER BY ((Current_price-prev_close)*100/Current_price) DESC LIMIT 5")
        for x in recommned:
            print(x.Name)
        
        curr_invest=0
        curr = 0 
        prev = 0
        
        #print(x.VALUE)
        for x in invested:
            curr_invest+=x.VALUE
        for x in investedtotal:
            stock_value = Stock.objects.get(ISIN=x.Stock_ISIN_id)
            curr+=x.Quantity*(stock_value.Current_price)
            prev+=x.Quantity*(stock_value.Prev_Close)

        pl =curr_invest-curr
        pl*=-1
        plper=0
        if(curr_invest!=0):
            plper = (pl/curr_invest)*100
        userdata=Stock.objects.all()

        return render(request,'index_dash.html',{"recommned":recommned,"curr":bankobj.Current_amount,"investordetails":investordetails,userdata:":userdata" ,'stokcs':stockobj,"userinvested":invested,"dashvals":[int(curr_invest),int(curr),int(pl),round(plper,2),prev]})
    else:   
        return HttpResponse('error',status=404)