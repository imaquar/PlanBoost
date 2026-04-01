from django.urls import path
from .views import RegisterView, CustomLoginView, profile, ChangePasswordView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True, template_name='registration/login.html'), name='login'),
    path('profile/', profile, name='profile'),
    path('password_change/', ChangePasswordView.as_view(), name='password_change'),
]