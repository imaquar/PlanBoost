from django.test import TestCase, Client
from . import views

class DashboardPageGetTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        url = '/'
        client = Client()
        cls.response = client.get(url)

    def test_url_access(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_name(self):
        self.assertEqual(self.response.resolver_match.url_name, 'dashboard')

    def test_url_namespace(self):
        self.assertEqual(self.response.resolver_match.namespace, 'dashboard')

    def test_view_name(self):
        self.assertEqual(self.response.resolver_match.func, views.index)
