"""Tests for the profile view."""
from django.test import TestCase
from django.urls import reverse
from clubs.forms import ApplicationForm
from clubs.models import User, Application, Club
from clubs.tests.helpers import reverse_with_next


class EditApplicationViewTest(TestCase):
    """Test suite for the Edit Profile view."""

    VIEW = 'edit_application'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        self.application = Application.objects.create(
            user=self.user,
            club=self.club,
            statement='Old Statement',
            status='pending'
        )
        self.form_input = {
            'statement': 'New Statement'
        }
        self.url = reverse(self.VIEW, kwargs={'application_id': self.application.id})

    def test_edit_application_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/{self.application.id}/')

    def test_get_edit_application(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplicationForm))
        self.assertFalse(form.is_bound)

    def test_get_application_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_statement_update(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     before_count = Application.objects.count()
    #     response = self.client.post(self.url, self.form_input, follow=True)
    #     after_count = Application.objects.count()
    #     self.assertEqual(after_count, before_count)
    #     response_url = reverse('view_applications')
    #     self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'view_applications.html')
    #     # form = response.context['form']
    #     # self.assertTrue(isinstance(form, ApplicationUpdateForm))
    #     # self.assertTrue(form.is_bound)
    #     self.application.refresh_from_db()
    #     self.assertEqual(self.application.statement, 'New Statement')

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
