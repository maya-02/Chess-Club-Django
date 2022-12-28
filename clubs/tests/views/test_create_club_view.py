from django.test import TestCase
from django.urls import reverse
from clubs.forms import ClubForm
from clubs.models import Club, User, Membership
from clubs.tests.helpers import reverse_with_next


class CreateClubViewTest(TestCase):
    """Tests of the create club view"""

    VIEW = 'create_club'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse(self.VIEW)
        self.form_input = {
            'name': 'alpha_bravo',
            'location': 'charlie delta',
            'description': 'echo foxtrot'
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/')

    def test_create_club_redirects_when_not_logged_in(self):
        before_count = Club.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)

    def test_get_create_club(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertFalse(form.is_bound)

    def test_create_club_makes_club(self):
        self.client.login(email=self.user.email, password="Password123")
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
        club = Club.objects.get(name='alpha_bravo')
        self.assertEqual(club.location, 'charlie delta')
        self.assertEqual(club.description, 'echo foxtrot')
        self.assertEqual(club.get_club_owner(), self.user)

    def test_unsuccessful_create_club(self):
        self.client.login(email=self.user.email, password="Password123")
        self.form_input['name'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertTrue(form.is_bound)
