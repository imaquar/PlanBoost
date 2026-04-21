from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from urllib.parse import quote

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


class UserLoginLogoutTests(TestCase):
    def setUp(self):
        self.username = 'authuser01'
        self.password = 'StrongPass123'
        self.user = User.objects.create_user(username=self.username, password=self.password,)

    def test_login_with_correct_credentials(self):
        response = self.client.post(
            reverse('users:login'),
            data={'username': self.username, 'password': self.password,},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:dashboard'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_with_incorrect_password(self):
        response = self.client.post(
            reverse('users:login'),
            data={'username': self.username, 'password': 'WrongPassword999',},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_ends_authenticated_session(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/users/login/')
        self.assertNotIn('_auth_user_id', self.client.session)


class LoginRequiredAccessTests(TestCase):
    def test_protected_pages_redirect_to_login_for_anonymous_user(self):
        protected_urls = [
            reverse('dashboard:dashboard'),
            reverse('notes:notes'),
            reverse('tasks:tasks'),
            reverse('timer:timer'),
            reverse('users:profile'),
        ]

        login_url = reverse('users:login')

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                expected_redirect = f'{login_url}?next={quote(url, safe="/")}'

                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)
