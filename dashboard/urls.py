from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('api/stats/', views.stats_ajax, name='stats_ajax'),
]