"""Unit tests of the log in form."""
from django import forms
from django.test import TestCase
from clubs.forms import LogInForm

"""5 Tests currently running"""


class LogInFormTestCase(TestCase):
    """Unit tests of the log in form."""

    def setUp(self):
        self.form_input = {'email': 'user@test.com', 'password': 'Password123'}

    def test_form_contains_required_fields(self):
        form = LogInForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        password_field = form.fields['password']
        self.assertTrue(isinstance(password_field.widget, forms.PasswordInput))

    def test_form_accepts_valid_input(self):
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_username(self):
        self.form_input['email'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # removed: test_form_accepts_incorrect_username

    def test_form_accepts_incorrect_password(self):
        self.form_input['password'] = 'pwd'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())
