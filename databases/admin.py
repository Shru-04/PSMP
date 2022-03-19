from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Stock)
admin.site.register(Investor)
admin.site.register(Bank)
admin.site.register(Company)
admin.site.register(Investment)