from django.db import models
from django.core.validators import *

# Create your models here.
class Stock(models.Model) :
    Name = models.CharField(max_length=1000)
    ISIN = models.CharField(max_length=1000,primary_key=True,unique=True)
    Volume = models.IntegerField()
    Prev_Close = models.FloatField()
    Day_low =  models.FloatField()
    Current_price =  models.FloatField()
    Beta =  models.FloatField()
    Regular_market_open =  models.FloatField()
    Day_high =  models.FloatField()
    Open =  models.FloatField()
    Revenue_growth =  models.FloatField()

class Investor(models.Model):
    Username = models.CharField(max_length=1000,primary_key=True,unique=True)
    Password = models.CharField(max_length=1000,unique=True)
    First_Name = models.CharField(max_length=1000)
    Last_Name = models.CharField(max_length=1000)
    Email_id = models.CharField(max_length=1000,validators=[validate_email],unique=True)
    Contact_no = models.CharField(max_length=13,unique=True)
    Pan_card_no = models.CharField(max_length=1000,unique=True)
    Address_Line = models.CharField(max_length=5000,default='empty')
    State = models.CharField(max_length=1000)
    city = models.CharField(max_length=1000)
    District = models.CharField(max_length=1000)
    Pin_code = models.IntegerField()
    #Stocks_Purchased = models.IntegerField(default=0)

class Bank(models.Model):
    Account_no = models.CharField(primary_key=True,max_length=1000,unique=True)
    Username = models.ForeignKey(Investor,on_delete=models.CASCADE,default='empty',unique=True)
    IFSC_code = models.CharField(max_length=1000)
    Branch = models.CharField(max_length=1000)
    Current_amount = models.IntegerField(default=0)

class Company(models.Model):
    Name = models.CharField(primary_key=True,max_length=1000,unique=True)
    Stock_ISIN = models.ForeignKey(Stock,on_delete=models.CASCADE,default='0')
    Sector = models.CharField(max_length=1000)
    Industry = models.CharField(max_length=10000,default='empty')
    Business_Summary = models.CharField(max_length=10000,default='empty')
    Website = models.URLField(default='empty')
    Gross_Profit = models.FloatField(default=0)

class Investment(models.Model):
    Quantity = models.IntegerField()
    Date_of_Purchased = models.DateField()
    #Invested_Amt = models.FloatField()
    Purchased_Value = models.FloatField()
    User_Account_no = models.ForeignKey(Bank,on_delete=models.CASCADE,default='empty')
    Stock_ISIN = models.ForeignKey(Stock,on_delete=models.CASCADE,default='0')
    Transaction_Mode= models.CharField(max_length=20,default='Buy')