"""Tests for the profile view."""
from django.test import TestCase
from django.urls import reverse
from clubs.forms import ProfileForm
from clubs.models import User
from clubs.tests.helpers import reverse_with_next


class EditProfileViewTest(TestCase):
    """Test suite for the Edit Profile view."""

    VIEW = 'edit_profile'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.other_user = User.objects.get(email='janedoe@example.org')
        self.url = reverse(self.VIEW)
        self.form_input = {
            'name': 'John Doe2',
            'email': 'johndoe2@example.org',
            'bio': 'New bio',
            'experience': 3
        }

    def test_edit_profile_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/')

    def test_get_profile(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_profile_update(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'BAD_EMAIL'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe@example.org')
        self.assertEqual(self.user.name, 'John Doe')
        self.assertEqual(self.user.experience, 2)
        self.assertEqual(self.user.bio, "Hello, I'm John Doe.")

    def test_unsuccessful_profile_update_due_to_duplicate_email(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'janedoe@example.org'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe@example.org')
        self.assertEqual(self.user.name, 'John Doe')
        self.assertEqual(self.user.experience, 2)
        self.assertEqual(self.user.bio, "Hello, I'm John Doe.")

    def test_successful_profile_update(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'John Doe2')
        self.assertEqual(self.user.experience, 3)
        self.assertEqual(self.user.email, 'johndoe2@example.org')
        self.assertEqual(self.user.bio, 'New bio')

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
