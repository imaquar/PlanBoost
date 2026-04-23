from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class TimerPageAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='timer_user', password='testpass123',)

    def test_anonymous_user_is_redirected_to_login(self):
        timer_url = reverse('timer:timer')
        login_url = reverse('login')

        response = self.client.get(timer_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{login_url}?next={timer_url}')

    def test_authenticated_user_can_open_timer_page(self):
        self.client.login(username='timer_user', password='testpass123')

        response = self.client.get(reverse('timer:timer'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'timer/timer.html')
