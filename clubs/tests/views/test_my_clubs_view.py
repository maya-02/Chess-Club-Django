from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, User, Membership
from clubs.tests.helpers import reverse_with_next


class MyClubsViewTest(TestCase):
    VIEW = 'my_clubs'  # like View My Applications

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.officer = User.objects.get(email='johndoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        officer_relationship = Membership.objects.create(
            user=self.officer,
            club=self.club,
            type=2
        )
        membership = Membership.objects.create(
            user=self.member,
            club=self.club,
            type=3
        )
        self.url = reverse(self.VIEW)

    def test_my_clubs_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/')

    def test_view_applications_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_my_clubs_contains_officer_case(self):
        self.client.login(email=self.officer.email, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, 'alpha_bravo')
        self.assertContains(response, 2)

    def test_my_clubs_contains_member_case(self):
        self.client.login(email=self.member.email, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, 'alpha_bravo')
        self.assertContains(response, 3)
