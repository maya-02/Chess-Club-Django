from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, User, Membership
from clubs.tests.helpers import reverse_with_next


class ClubListViewTest(TestCase):
    """Tests of the view application for club view"""

    CLUB_COUNT = 15
    VIEW = 'club_list'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse(self.VIEW)

    def test_club_list_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/')

    def test_club_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # !!!
    def test_get_club_list(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_club(self.CLUB_COUNT)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        self.assertEqual(len(response.context['clubs']), self.CLUB_COUNT)

        # for club_id in range(15):
        #     self.assertContains(response, f'Name{club_id}')
        #     self.assertContains(response, f'Location{club_id}')
        #     self.assertContains(response, f'Description{club_id}')

    def _create_test_club(self, club_count=10):
        for club_id in range(club_count):
            test_owner = User.objects.create_user(
                name=f'name{club_id}',
                email=f'email{club_id}@test.com',
                password='Testing123'
            )
            test_club = Club.objects.create(
                name=f'Name{club_id}',
                location=f'Location{club_id}',
                description=f'Description{club_id}',
            )
            ownership = Membership.objects.create(
                user=test_owner,
                club=test_club,
                type=1
            )
