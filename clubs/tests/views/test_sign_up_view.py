"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import SignUpForm
from clubs.models import User
from clubs.tests.helpers import LogInTester


class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view."""

    VIEW = 'sign_up'

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse(self.VIEW)
        self.user = User.objects.get(email='johndoe@example.org')
        self.form_input = {
            'name': 'Jane Doe',
            'email': 'janedoe@example.org',
            'experience': 1,
            'bio': 'My bio',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }
        self.user = User.objects.get(email='johndoe@example.org')

    def test_sign_up_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/')

    def test_get_sign_up_redirects_when_logged_in(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_sign_up(self):
        self.form_input['email'] = 'BAD_EMAIL'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
        user = User.objects.get(email='janedoe@example.org')
        self.assertEqual(user.name, 'Jane Doe')
        self.assertEqual(user.experience, 1)
        self.assertEqual(user.bio, 'My bio')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())
