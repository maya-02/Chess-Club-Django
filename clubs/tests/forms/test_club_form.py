from django.test import TestCase
from clubs.forms import ClubForm
from clubs.models import Club, User, Membership
from django import forms


class ClubFormTestCase(TestCase):
    """Unit tests for Club Form"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.form_input = {
            'name': 'alpha_bravo',
            'location': 'charlie delta',
            'description': 'echo foxtrot'
        }

    def test_club_is_made(self):
        self.client.login(username=self.user.email, password="Password123")
        form = ClubForm(data=self.form_input)
        before_count = Club.objects.count()
        form.save(self.user)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        club = Club.objects.get(name='alpha_bravo')
        self.assertEqual(club.name, 'alpha_bravo')
        self.assertEqual(club.location, 'charlie delta')
        self.assertEqual(club.description, 'echo foxtrot')

    def test_club_owner_is_set(self):
        self.client.login(username=self.user.email, password="Password123")
        form = ClubForm(data=self.form_input)
        before_count = Membership.objects.count()
        form.save(self.user)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count + 1)
        club = Club.objects.get(name='alpha_bravo')
        membership = Membership.objects.get(user=self.user, club=club)
        self.assertEqual(membership.type, 1)

    def test_valid_club_form(self):
        form = ClubForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_name_has_charfield(self):
        form = ClubForm()
        name = form.fields['name']
        self.assertTrue(isinstance(name, forms.CharField))

    def test_location_has_charfield(self):
        form = ClubForm()
        location = form.fields['location']
        self.assertTrue(isinstance(location, forms.CharField))

    def test_description_has_charfield(self):
        form = ClubForm()
        description = form.fields['description']
        self.assertTrue(isinstance(description, forms.CharField))

    def test_form_uses_name_validation(self):
        self.form_input['name'] = 'a' * 21
        form = ClubForm(self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_uses_location_validation(self):
        self.form_input['location'] = 'a' * 41
        form = ClubForm(self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_uses_description_validation(self):
        self.form_input['name'] = 'a' * 521
        form = ClubForm(self.form_input)
        self.assertFalse(form.is_valid())
