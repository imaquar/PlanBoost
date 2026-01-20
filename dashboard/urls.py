from django.urls import path
from dashboard import views

urlpatterns = [
    path('', views.index),
    path('notes/', views.notes),
    path('tasks/', views.tasks),
    path('timer/', views.timer),
]