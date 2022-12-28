from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, User, Application, Membership
from clubs.tests.helpers import reverse_with_next


class ChangeAppStatusViewTestCase(TestCase):
    """Tests of the change application status view"""
    VIEW = 'change_app_status'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.user_one = User.objects.get(email='petrapickles@example.org')
        self.user_two = User.objects.get(email='peterpickles@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        ownership = Membership.objects.create(
            user=self.owner,
            club=self.club,
            type=1
        )
        self.application_one = Application.objects.create(
            user=self.user_one,
            club=self.club,
            status='pending'
        )
        self.application_two = Application.objects.create(
            user=self.user_two,
            club=self.club,
            status='pending'
        )
        self.accept_one_url = reverse(self.VIEW, kwargs={'application_id': self.application_one.id, 'accept': 1,
                                                         'club_id': self.club.id})
        self.reject_two_url = reverse(self.VIEW, kwargs={'application_id': self.application_two.id, 'accept': 0,
                                                         'club_id': self.club.id})

    def test_change_app_status_url(self):
        self.assertEqual(self.accept_one_url, f'/{self.VIEW}/{self.application_one.id}/1/{self.club.id}/')
        self.assertEqual(self.reject_two_url, f'/{self.VIEW}/{self.application_two.id}/0/{self.club.id}/')

    def test_change_app_status_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.accept_one_url)
        response = self.client.get(self.accept_one_url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        redirect_url = reverse_with_next('log_in', self.reject_two_url)
        response = self.client.get(self.reject_two_url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_change_app_status_accepts_application(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        member_before_count = Membership.objects.count()
        response = self.client.get(self.accept_one_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count + 1)
        self.application_one.refresh_from_db()
        self.assertEqual(self.application_one.status, 'accepted')

    def test_change_app_status_rejects_application(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        member_before_count = Membership.objects.count()
        response = self.client.get(self.reject_two_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count)
        self.application_two.refresh_from_db()
        self.assertEqual(self.application_two.status, 'rejected')
