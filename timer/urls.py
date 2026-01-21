from django.urls import path
from timer import views

app_name = 'timer'

urlpatterns = [
    path('', views.index, name ='timer'),
]