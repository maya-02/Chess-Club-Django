from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from clubs.models import Club, User, Tournament, Membership
from clubs.forms import TournamentForm
from clubs.tests.helpers import reverse_with_next


class CreateTournamentViewTest(TestCase):
    """Tests of the log out view."""

    VIEW = 'create_tournament'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        Membership.objects.create(
            user=self.user,
            club=self.club,
            type=2
        )
        self.form_input = {
            'name': 'testing',
            'description': 'testing description',
            'deadline': '2025-10-25',
            'capacity': 2,
            'organiser': self.user,
            'club': self.club
        }
        self.url = reverse(self.VIEW, kwargs={'club_id': self.club.id})

    def test_create_tournament_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/{self.club.id}/')

    def test_create_tournament_redirects_when_not_logged_in(self):
        before_count = Tournament.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)

    def test_get_create_tournament(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TournamentForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_create_tournament(self):
        self.client.login(email=self.user.email, password="Password123")
        self.form_input['capacity'] = 1
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TournamentForm))
        self.assertTrue(form.is_bound)

    def test_successful_create_tournament(self):
        self.client.login(email=self.user.email, password="Password123")
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        tournament = Tournament.objects.get(name='testing')
        self.assertEqual(tournament.description, 'testing description')
        self.assertEqual(tournament.deadline, datetime(2025, 10, 25, 0, 0))
        self.assertEqual(tournament.capacity, 2)
        self.assertEqual(tournament.club, self.club)
