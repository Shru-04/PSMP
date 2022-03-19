from django.urls import path
from django.conf import urls
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'databases'
urlpatterns = [
    path('',views.index,name='index'),
    path('stocks',views.stock_manage,name='stocks'),
    path('userstock',views.user_stock,name='userstock'),
    path('filldb',views.fill_db,name='filldb'),
    path('filldb2',views.fill_db2,name='filldb2'),
    path('apidata',views.redis_data,name='apidata'),
    path('buy_sell',views.buyupdate,name='buy_sell'),
    path('sell',views.sellupdate,name='sell'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)