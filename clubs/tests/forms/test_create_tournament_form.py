from django.test import TestCase
from clubs.forms import TournamentForm
from clubs.models import Application, User, Club, Membership, Tournament
from django import forms
import datetime


# Testing the creation of a tournament is successful
class TournamentFormTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        self.form_input = {
            'name': 'testing2',
            'description': 'testing',
            'deadline':'2025-10-25',
            'capacity':2,
            'club':self.club
        }

    def test_valid_create_tournament_form(self):
        form = TournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_name_is_charfield(self):
        form = TournamentForm()
        name = form.fields['name']
        self.assertTrue(isinstance(name, forms.CharField))

    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_description_is_charfield(self):
        form = TournamentForm()
        description = form.fields['description']
        self.assertTrue(isinstance(description, forms.CharField))

    def test_form_rejects_blank_description(self):
        self.form_input['description'] = ''
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_capacity_is_integerfield(self):
        form = TournamentForm()
        capacity = form.fields['capacity']
        self.assertTrue(isinstance(capacity, forms.IntegerField))

    def test_form_rejects_blank_capacity(self):
        self.form_input['capacity'] = ''
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_capacity_less_than_2(self):
        self.form_input['capacity'] = 1
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_capacity_more_than_96(self):
        self.form_input['capacity'] = 97
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_deadline(self):
        self.form_input['deadline'] = ''
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_today_deadline(self):
        self.form_input['deadline'] = datetime.date.today()
        form = TournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_past_deadline(self):
        self.form_input['deadline'] = '2000-11-11'
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_future_deadline(self):
        self.form_input['deadline'] = datetime.date.today() + datetime.timedelta(days=1)
        form = TournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_deadline_is_datefield(self):
        form = TournamentForm()
        deadline = form.fields['deadline']
        self.assertTrue(isinstance(deadline, forms.DateField))

    def test_create_tournament_form_must_save_correctly(self):
        self.client.login(email=self.user.email, password="Password123")
        form = TournamentForm(data=self.form_input)
        before_count = Tournament.objects.count()
        form.save(self.club, self.user)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)
        tournament = Tournament.objects.get(name='testing2')
        self.assertEqual(tournament.name, 'testing2')
        self.assertEqual(tournament.description, 'testing')
        self.assertEqual(tournament.deadline, datetime.datetime(2025, 10, 25, 0, 0))
        self.assertEqual(tournament.capacity, 2)
        self.assertEqual(tournament.club, self.club)
