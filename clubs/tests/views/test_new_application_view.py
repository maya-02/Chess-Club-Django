from django.test import TestCase
from django.urls import reverse
from clubs.forms import ApplicationForm
from clubs.models import Club, User, Application, Membership
from clubs.tests.helpers import reverse_with_next


class NewApplicationViewTestCase(TestCase):
    """Tests of the club application sign up view"""
    VIEW = 'new_application'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        ownership = Membership.objects.create(
            user=self.owner,
            club=self.club,
            type=1
        )
        self.url = reverse(self.VIEW, kwargs={'club_id': self.club.id})
        self.data = {
            'statement': 'Hello I would like to join this club'
        }

    def test_new_application_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/{self.club.id}/')

    def test_new_application_redirects_when_not_logged_in(self):
        before_count = Application.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_get_new_application(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplicationForm))
        self.assertFalse(form.is_bound)

    def test_club_exists(self):
        self.assertTrue(isinstance(self.club, Club))
        self.assertEqual(self.club.id, 1)
        self.assertEqual(self.club.name, 'alpha_bravo')

    def test_new_application_is_made(self):
        self.client.login(username=self.user.email, password="Password123")
        before_count = Application.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('club_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_list.html')
        application = Application.objects.get(user=self.user, club=self.club)
        self.assertEqual(application.statement, 'Hello I would like to join this club')
        self.assertEqual(application.status, 'pending')
