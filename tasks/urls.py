from django.urls import path
from tasks import views

app_name = 'tasks'

urlpatterns = [
    path('', views.index, name='tasks'),
    path('task/<int:id>/', views.task, name='task'),
    path('create/', views.create, name='create'),
    path('edit/<int:id>/', views.edit, name='edit'),
]