from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, User, Membership
from clubs.tests.helpers import reverse_with_next


class ClubMembersViewTest(TestCase):
    """Tests for Club Members view"""

    VIEW = 'club_members'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.officer = User.objects.get(email='janedoe@example.org')
        self.member = User.objects.get(email='petrapickles@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        ownership = Membership.objects.create(
            user=self.owner,
            club=self.club,
            type=1
        )
        officer_relationship = Membership.objects.create(
            user=self.officer,
            club=self.club,
            type=2
        )
        membership = Membership.objects.create(
            user=self.member,
            club=self.club,
            type=3
        )
        self.url = reverse(self.VIEW, kwargs={'club_id': self.club.id})

    def test_club_members_url(self):
        self.assertEqual(self.url, f'/{self.VIEW}/{self.club.id}/')

    def test_club_members_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_club_members_contains_set_up_cases_for_owner(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, self.owner.name)
        self.assertContains(response, self.officer.name)
        self.assertContains(response, self.member.name)

    def test_club_memberss_contains_set_up_cases_for_officer(self):
        self.client.login(email=self.officer.email, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, self.owner.name)
        self.assertContains(response, self.officer.name)
        self.assertContains(response, self.member.name)

    def test_club_members_contains_set_up_cases_for_member(self):
        self.client.login(email=self.member.email, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, self.owner.name)
        self.assertContains(response, self.officer.name)
        self.assertContains(response, self.member.name)
