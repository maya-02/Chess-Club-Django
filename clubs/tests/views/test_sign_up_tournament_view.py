from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from clubs.models import Club, User, TournamentMembers, Tournament, Membership
from clubs.tests.helpers import reverse_with_next


class SignUpTournamentViewTestCase(TestCase):
    """Tests of the log out view."""

    VIEW = 'sign_up_tournament'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.organiser = User.objects.get(email='johndoe@example.org')
        self.user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        self.ownership = Membership.objects.create(
            user=self.organiser,
            club=self.club,
            type=1
        )
        self.membership = Membership.objects.create(
            user=self.user,
            club=self.club,
            type=3
        )
        self.tournament = Tournament.objects.create(
            name='test',
            organiser=self.organiser,
            description='test',
            deadline='2026-10-25 14:30:59',
            capacity=3,
            club=self.club)
        self.url = reverse(self.VIEW, kwargs={'tournament_id': self.tournament.id})

    def test_create_tournament_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/{self.tournament.id}/')

    def test_sign_up_tournament_redirects_when_not_logged_in(self):
        before_count = TournamentMembers.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = TournamentMembers.objects.count()
        self.assertEqual(after_count, before_count)

    def test_get_sign_up_tournament(self):
        self.client.login(email=self.user.email, password='Password123')
        redirect_url = reverse_with_next('tournament_list', self.url)
        before_count = TournamentMembers.objects.count()
        response = self.client.get(self.url)
        after_count = TournamentMembers.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.tournament.is_contestant(self.user)
        # self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        # self.assertTemplateUsed(response, f'tournament_list.html')
