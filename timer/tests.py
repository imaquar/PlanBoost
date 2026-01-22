from django.test import TestCase, Client
from . import views

class TimerPageGetTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        url = '/timer/'
        client = Client()
        cls.response = client.get(url)

    def test_url_access(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_name(self):
        self.assertEqual(self.response.resolver_match.url_name, 'timer')

    def test_url_namespace(self):
        self.assertEqual(self.response.resolver_match.namespace, 'timer')

    def test_view_name(self):
        self.assertEqual(self.response.resolver_match.func, views.index)
