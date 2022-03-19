from django.shortcuts import render
from databases.models import *
from django import forms

# Create your views here.
def index(request):
    context = {}
    check_user = Bank.objects.filter(Username=request.user.username).exists()
    check_user2 = Investor.objects.filter(Username=request.user.username).exists()
    context['check_investor'] = check_user
    context['check_investor2'] = check_user2
    return render(request,'index.html',context)