from clubs.models import User, Club, Membership
from django.test import TestCase


class MembershipModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.other_user_one = User.objects.get(email='janedoe@example.org')
        self.other_user_two = User.objects.get(email='petrapickles@example.org')
        self.test_club = Club.objects.get(name='alpha_bravo')

    def test_get_type(self):
        ownership = Membership.objects.create(user=self.user, club=self.test_club, type=1)
        officer_relationship = Membership.objects.create(user=self.other_user_one, club=self.test_club, type=2)
        membership = Membership.objects.create(user=self.other_user_two, club=self.test_club, type=3)
        self.assertEqual(ownership.get_type(), 'owner')
        self.assertEqual(officer_relationship.get_type(), 'officer')
        self.assertEqual(membership.get_type(), 'member')
