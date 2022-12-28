from django.test import TestCase
from clubs.forms import ApplicationForm
from clubs.models import Application, User, Club, Membership
from django import forms


# Testing the creation of a club is successful
class ApplicationFormTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        self.form_input = {
            'user': self.user,
            'club': self.club,
            'statement': 'Hello, I would like to join this club'
        }

    def test_valid_application_form(self):
        form = ApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_statement_is_charfield(self):
        form = ApplicationForm()
        name = form.fields['statement']
        self.assertTrue(isinstance(name, forms.CharField))

    def test_form_rejects_blank_statement(self):
        self.form_input['statement'] = ''
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_application_form_must_save_correctly(self):
        self.client.login(username=self.user.email, password="Password123")
        form = ApplicationForm(data=self.form_input)
        before_count = Application.objects.count()
        form.save(self.user, self.club)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        application = Application.objects.get(user=self.user, club=self.club)
        self.assertEqual(application.statement, 'Hello, I would like to join this club')
        self.assertEqual(application.status, 'pending')
