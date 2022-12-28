from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, User, Application
from clubs.tests.helpers import reverse_with_next


class ViewApplicationTestCase(TestCase):
    VIEW = 'view_applications'  # like View My Applications

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        application = Application.objects.create(
            user=self.user,
            club=self.club,
            status='pending'
        )
        self.url = reverse(self.VIEW)

    def test_view_applications_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/')

    def test_view_applications_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_view_applications_contains_set_up_case(self):
        self.client.login(username=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, 'alpha_bravo')
        self.assertContains(response, 'pending')
