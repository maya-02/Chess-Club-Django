"""Tests of the log out view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.tests.helpers import LogInTester


class LogOutViewTestCase(TestCase, LogInTester):
    """Tests of the log out view."""

    VIEW = 'log_out'

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse(f'{self.VIEW}')
        self.user = User.objects.get(email='johndoe@example.org')

    def test_log_out_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/')

    def test_get_log_out(self):
        self.client.login(username=self.user.email, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())
