from django.urls import path
from notes import views

app_name = 'notes'

urlpatterns = [
    path('', views.index, name='notes'),
    path('note/<int:id>/', views.note, name='note'),
    path('create/', views.create, name='create'),
]