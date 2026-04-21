from django.test import TestCase
from django.urls import reverse


class AuthenticationPagesTests(TestCase):
    def test_login_page_is_available_and_uses_template(self):
        response = self.client.get(reverse('users:login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_register_page_is_available_and_uses_template(self):
        response = self.client.get(reverse('users:register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
