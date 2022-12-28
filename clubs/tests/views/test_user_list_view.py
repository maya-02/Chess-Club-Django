from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.tests.helpers import reverse_with_next


class UserListTest(TestCase):
    """Tests for User List view"""

    USERS_CREATED_COUNT = 15
    CONSTANT = User.objects.count() + 1  # Trying to make sure there is no interference with current database
    VIEW = 'user_list'

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse(self.VIEW)
        self.user = User.objects.get(email='johndoe@example.org')  # Counts as 1 user

    def test_user_list_url(self):
        self.assertEqual(self.url, '/users/')

    def test_get_user_list(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_users(self.USERS_CREATED_COUNT)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        self.assertEqual(len(response.context['users']), self.USERS_CREATED_COUNT + 1)
        for user_id in range(self.CONSTANT, self.CONSTANT + self.USERS_CREATED_COUNT):
            user = User.objects.get(email=f'user{user_id}@test.org')
            self.assertContains(response, f'Name{user_id}')

    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

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
