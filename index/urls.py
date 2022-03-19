from django.urls import path
from django.conf.urls.static import static
from django.conf import settings, urls

from . import views

app_name = 'index'

urlpatterns = [
    path('',views.index,name='index'),
    #urls.url('',views.UserFormView.as_view(),name='logins'),
]