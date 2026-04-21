from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .forms import RegisterForm


class AuthenticationPagesTests(TestCase):
    def test_login_page_is_available_and_uses_template(self):
        response = self.client.get(reverse('users:login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_register_page_is_available_and_uses_template(self):
        response = self.client.get(reverse('users:register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')


class UserRegistrationFormTests(TestCase):
    def test_register_form_is_valid_with_correct_data(self):
        form = RegisterForm(
            data={'username': 'newuser01', 'password1': 'StrongPass123', 'password2': 'StrongPass123',}
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_register_post_creates_user_with_correct_data(self):
        response = self.client.post(
            reverse('users:register'),
            data={'username': 'newuser02', 'password1': 'StrongPass123', 'password2': 'StrongPass123',},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username='newuser02').exists())
