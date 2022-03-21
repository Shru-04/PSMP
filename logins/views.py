from django.contrib.auth import authenticate, login, logout,password_validation
from django.shortcuts import redirect, render
from django.http import HttpResponse, response,HttpResponseRedirect
from django.views.generic import View
from django.views import generic
from .models import *
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail
import random,string
from databases.models import *

# Create your views here.
def index(request):
    return render(request,'home.html')

def user_login(request):
    form = UserForm(request.POST)
    template_name = 'home.html'
    context = {}
    context['form'] = form
    print(request.POST)
    if form.is_valid():
        #user = form.save(commit=False)    
        username = request.POST['username']
        password = request.POST['password']
        #user.set_password(password)
        #user.save()
        print(username)
        user = authenticate(request,password=password,username=username) 
        #logout(request)
        if user is not None:
             login(request,user)
             messages.success(request,"Logged in Successfully !!")
             return redirect('index:index')
        else:
             #return HttpResponse("<h1> Invalid Credentials </h1>")
             messages.error(request,"Invalid Credentials !!")
    return render(request,template_name,context)
    
def user_logout(request):
    print(request.POST)
    template_name = 'index.html'
    logout(request)
    messages.success(request,"You are Logged Out") 
    return redirect('index:index')
    #return render(request,template_name)

def user_reg(request):
    try:
        form = UserForm(request.POST)
        template_name = 'signup.html'
        context = {}
        context['form'] = form
        print(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            fn = form.cleaned_data['first_name']
            email = form.cleaned_data['email']
            if (password != confirm_password or User.objects.filter(email=email).exists() or User.objects.filter(password=password).exists() or User.objects.filter(first_name=fn).exists()):
                print(1)
                raise ValidationError(
                    "password and confirm_password does not match"
                )
            else:
                # user = form.save(commit=False)
                # user.set_password(password)
                # user.save()
                user = User.objects.create_user(username,email,confirm_password)
                if password_validation.validate_password(confirm_password,user) is not None:
                    print("123")
                    raise ValidationError("The password is too similar to the username. This password is too short. It must contain at least 8 characters.")
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.set_password(password)
                user.save()
                messages.success(request,"Successfully Registered")
                return redirect('index:index')
        else:
            #form = UserForm()
            #return HttpResponse("Invalid <a href = 'register'> go back </a>")
            messages.info(request,"Please Fill the Details Properly")
    except ValidationError:
        print(Exception)
        messages.error(request,"Invalid Credentials, Maybe Redundancy or error in fields")
        form = UserForm()
        #return HttpResponse("<h1>Invalid Credentials, Maybe Redundancy or error in fields <a href = 'register'> go back </a></h1>")
    return render(request,template_name,context)

def user_reset(request):
    form = UserForm(request.POST)
    template_name = 'reset.html'
    context = {}
    context['form'] = form
    print(request.POST)
    x = ''.join(random.choices(string.ascii_letters + string.digits + '@',k=10))
    if form.is_valid():
        print("123")
        email = form.cleaned_data['email']
        #x = form.cleaned_data['password']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            if password_validation.validate_password(x,user) is None:
                print(user.first_name)
                user.set_password(x)
                user.save()
                send_mail('New Password Reset',f'Hi {user.first_name} Your new password is {x} and is successfully reseted. Note that this will be your password unless resetted again. If you want to change the password to your convenience, contact this email.',from_email=None,recipient_list=[email])
                messages.success(request,"Succesfully Sent, check mail (if its in spam otherwise) n <a href='reset/login'> login </a></h1>")
                #return HttpResponse("<h1> Done, check mail (if its in spam otherwise) n <a href='reset/login'> login </a></h1>")
            else:
                messages.error(request,"Error User not Found")
                #return HttpResponse('error')
        else:
            #return HttpResponse('error')
            messages.error(request,"error")
    else:
        messages.info(request,"Please Fill the Details Properly")
    return render(request,template_name,context)

def investor_reg(request):
    if User.is_authenticated:
        if request.method == 'POST' and Investor.objects.filter(Username=request.user.username).exists() is True:
            redirect('register_bank')
        elif request.method == 'POST':
            i = Investor()
            i.Username = request.user.username
            i.Email_id = request.user.email
            i.First_Name = request.user.first_name
            i.Last_Name = request.user.last_name
            i.Password = request.user.password
            i.Pan_card_no = request.POST['Pan_card_no']
            i.Address_Line = request.POST['Address_Line']
            i.State = request.POST['State']
            i.city = request.POST['city']
            i.District = request.POST['District']
            i.Pin_code = request.POST['Pin_code']
            i.Contact_no = request.POST['Contact_no']
            context = {}
            context['investor'] = i
            #return HttpResponse("ok")
            print(request.POST)
            print(str(i.Username))
            req = request.POST.dict()
            try:
                i.clean_fields()
                if Investor.objects.filter(Username = i.Username).exists():
                    raise ValidationError("Problem")
                for itr in req.keys():
                    if (req[itr] == ''):
                        raise ValidationError("Problem")
                i.save()
                if Investor.objects.filter(Username=request.user.username).exists() is True:
                    return redirect('register_bank')
            except ValidationError:
                print(ValidationError)
                i = Investor()
                messages.error(request,"Error")
                #return HttpResponse("<h1> Error </h1>")
            return render(request,'signup_invest.html',context)
        else:
            return render(request,'signup_invest.html')
    else:
        return HttpResponse("Error")

def bank_reg(request):
    if User.is_authenticated and Investor.objects.filter(Username = request.user.username).exists() is True:
        if request.method == 'POST':
            i = Bank()
            i.Username = Investor.objects.get(Username = request.user.username)
            i.Account_no = request.POST['Account_no']
            i.IFSC_code = request.POST['IFSC_code']
            i.Branch = request.POST['Branch']
            i.Current_amount = request.POST['Current_amount']
            context = {}
            context['investor'] = i
            #return HttpResponse("ok")
            print(request.POST)
            print(str(i.Branch))
            req = request.POST.dict()
            try:
                i.clean_fields()
                if Bank.objects.filter(Account_no = i.Account_no).exists():
                    raise ValidationError("Problem")
                for itr in req.keys():
                    if (req[itr] == ''):
                        raise ValidationError("Problem")
                i.save()
                if Bank.objects.filter(Username=request.user.username).exists() is True:
                    messages.success(request,"Your all set to go...")
                    return redirect('index:index')
            except ValidationError:
                print(ValidationError)
                messages.error("Error !!")
                i = Bank()
                #return HttpResponse("<h1> Error <a href = 'register_bank'> go back </a></h1>")
            return render(request,'signup_bank.html',context)
        else:
            return render(request,'signup_bank.html')
    else:
        return HttpResponse("Error")
    





