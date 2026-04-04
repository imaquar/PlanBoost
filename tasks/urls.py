from django.urls import path
from tasks import views

app_name = 'tasks'

urlpatterns = [
    path('', views.index, name='tasks'),
    path('task/<int:id>/', views.task, name='task'),
    path('create/', views.create, name='create'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('toggle-status/<int:id>/', views.toggle_status, name='toggle_status'),
]