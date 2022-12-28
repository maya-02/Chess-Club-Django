"""Unit tests of the sign up form."""
from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from clubs.forms import SignUpForm
from clubs.models import User

"""4 Tests currently running"""


class SignUpFormTestCase(TestCase):
    """Unit tests of the sign up form."""

    def setUp(self):
        self.form_input = {
            'name': 'Jane Doe',
            'email': 'janedoe@example.org',
            'experience': 2,
            'bio': 'My bio',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('name', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('experience', form.fields)
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    # def test_form_uses_model_validation(self):
    #     self.form_input['username'] = 'badusername'
    #     form = SignUpForm(data=self.form_input)
    #     self.assertFalse(form.is_valid())

    """not implemented yet"""

    # def test_password_must_contain_uppercase_character(self):
    #     self.form_input['new_password'] = 'password123'
    #     self.form_input['password_confirmation'] = 'password123'
    #     form = SignUpForm(data=self.form_input)
    #     self.assertFalse(form.is_valid())

    # def test_password_must_contain_lowercase_character(self):
    #     self.form_input['new_password'] = 'PASSWORD123'
    #     self.form_input['password_confirmation'] = 'PASSWORD123'
    #     form = SignUpForm(data=self.form_input)
    #     self.assertFalse(form.is_valid())

    # def test_password_must_contain_number(self):
    #     self.form_input['new_password'] = 'PasswordABC'
    #     self.form_input['password_confirmation'] = 'PasswordABC'
    #     form = SignUpForm(data=self.form_input)
    #     self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SignUpForm(data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        user = User.objects.get(email='janedoe@example.org')
        self.assertEqual(user.name, 'Jane Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.experience, 2)
        self.assertEqual(user.bio, 'My bio')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)