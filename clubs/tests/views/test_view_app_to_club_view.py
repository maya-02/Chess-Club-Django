from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, User, Application, Membership
from clubs.tests.helpers import reverse_with_next


class ViewAppToClubViewTestCase(TestCase):
    """Tests of the view application for club view"""
    APPLICATION_COUNT = 5
    CONSTANT = User.objects.count() + 1  # Trying to make sure there is no interference with current database
    VIEW = 'view_app_to_club'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        ownership = Membership.objects.create(
            user=self.owner,
            club=self.club,
            type=1
        )
        self.url = reverse(self.VIEW, kwargs={'club_id': self.club.id})

    def test_club_application_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/{self.club.id}/')

    def test_view_app_to_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # !!!
    def test_get_club_application_list(self):
        self.client.login(email=self.owner.email, password='Password123')
        before_count = Application.objects.filter(club=self.club).count()
        self._create_test_applications(self.APPLICATION_COUNT)
        after_count = Application.objects.filter(club=self.club).count()
        self.assertEqual(after_count, before_count + self.APPLICATION_COUNT)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')

        # for user in range(self.APPLICATION_COUNT):
        #     user_id=user+self.CONSTANT
        #     self.assertContains(response, f'Name{user_id}')
        #     self.assertContains(response, f'Statement {user_id}')
        #     user = User.objects.get(email=f'user{user_id}@test.org')
        #     user_url = reverse('show_user', kwargs={'user_id': user.id})
        #     self.assertContains(response, user_url)

    def _create_test_users(self, user_count):
        for user in range(user_count):
            user_id = user + self.CONSTANT
            User.objects.create_user(
                email=f'user{user_id}@test.org',
                password='Password123',
                name=f'Name{user_id}',
                experience=1,
                bio=f'Bio {user_id}'
            )

    # Makes a number of users that will make applications to self.club
    def _create_test_applications(self, application_count=5):
        self._create_test_users(application_count)
        for user in range(application_count):
            user_id = user + self.CONSTANT
            Application.objects.create(
                user=User.objects.get(email=f'user{user_id}@test.org'),
                club=self.club,
                statement=f'Statement {user_id}'
            )
