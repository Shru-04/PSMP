from django.urls import path
from django.conf import urls
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'prediction'
urlpatterns = [
    path('',views.index,name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)