from django.test import TestCase
from clubs.models import User, Club, Membership, Application


class ClubModelTestCase(TestCase):
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
        self.other_user_three = User.objects.get(email='peterpickles@example.org')
        self.test_club = Club.objects.get(name='alpha_bravo')
        self.ownership = Membership.objects.create(user=self.user, club=self.test_club, type=1)
        self.membership_one = Membership.objects.create(user=self.other_user_one, club=self.test_club, type=3)

    def test_get_owner(self):
        self.assertEqual(self.test_club.get_club_owner(), self.user)
        self.assertNotEqual(self.test_club.get_club_owner(), self.other_user_one)

    def test_num_of_applications(self):
        before_count = self.test_club.num_of_applications()
        self.assertEqual(before_count, 0)
        application = Application.objects.create(user=self.other_user_three, club=self.test_club, statement='Hello',
                                                 status='pending')
        after_count = self.test_club.num_of_applications()
        self.assertEqual(after_count, before_count + 1)

    def test_num_of_members(self):
        before_count = self.test_club.num_of_members()
        self.assertEqual(before_count, 2)  # owner and membership_one
        membership_two = Membership.objects.create(user=self.other_user_two, club=self.test_club, type=3)
        self.test_club.refresh_from_db()
        after_count = self.test_club.num_of_members()
        self.assertEqual(after_count, before_count + 1)
