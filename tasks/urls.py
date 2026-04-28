from django.urls import path
from tasks import views

app_name = 'tasks'

urlpatterns = [
    path('', views.index, name='tasks'),
    path('task/<int:id>/', views.task, name='task'),
    path('create/', views.create, name='create'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('toggle-status-ajax/<int:id>/', views.toggle_status_ajax, name='toggle_status_ajax'),
    path('api/list/', views.tasks_list_ajax, name='tasks_list_ajax'),
    path('api/filter/', views.tasks_filter_ajax, name='tasks_filter_ajax'),
    path('api/stats/', views.stats, name='stats'),
]
