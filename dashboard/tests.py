from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dashboard_user', password='testpass123',)

    def test_anonymous_user_is_redirected_to_login(self):
        dashboard_url = reverse('dashboard:dashboard')
        login_url = reverse('login')

        response = self.client.get(dashboard_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{login_url}?next={dashboard_url}')

    def test_authenticated_user_can_open_dashboard(self):
        self.client.login(username='dashboard_user', password='testpass123')

        response = self.client.get(reverse('dashboard:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
