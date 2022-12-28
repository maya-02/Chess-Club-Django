"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from clubs.forms import ProfileForm
from clubs.models import User

"""3 Tests currently running"""


class ProfileFormTestCase(TestCase):
    """Unit tests of the profile form."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.form_input = {
            'name': 'Jane Doe',
            'email': 'janedoe@example.org',
            'experience': 2,
            'bio': 'My bio',
        }

    def test_form_has_necessary_fields(self):
        form = ProfileForm()
        self.assertIn('name', form.fields)
        self.assertIn('experience', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)

    def test_valid_user_form(self):
        form = ProfileForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # # !!!
    # def test_form_uses_model_validation(self):
    #     self.form_input['username'] = 'badusername'
    #     form = UserForm(data=self.form_input)
    #     self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(email='johndoe@example.org')
        form = ProfileForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.name, 'Jane Doe')
        self.assertEqual(user.experience, 2)
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.bio, 'My bio')
