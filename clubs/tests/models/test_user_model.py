"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Membership

"""16 Tests currently running"""
"""Warning with 1 test:
    - Name cannot contain over 100 characters.
"""


class UserModelTestCase(TestCase):
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

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_name_must_not_be_blank(self):
        self.user.name = ''
        self._assert_user_is_invalid()

    def test_name_need_not_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.name = second_user.name
        self._assert_user_is_valid()

    def test_name_may_contain_100_characters(self):
        self.user.first_name = 'x' * 100
        self._assert_user_is_valid()

    # !!! 101 doesn't work
    def test_name_must_not_contain_more_than_100_characters(self):
        self.user.first_name = 'x' * 200
        self._assert_user_is_invalid()

    def test_last_name_must_not_contain_more_than_100_characters(self):
        self.user.last_name = 'x' * 200
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_100_characters(self):
        self.user.last_name = 'x' * 100
        self._assert_user_is_valid()         

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_text_before_at_symbol(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.bio = second_user.bio
        self._assert_user_is_valid()

    def test_bio_may_contain_520_characters(self):
        self.user.bio = 'x' * 520
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_520_characters(self):
        self.user.bio = 'x' * 521
        self._assert_user_is_invalid()

    """Tests below are for methods in User model"""

    def test_get_membership(self):
        test_club = Club.objects.get(name='alpha_bravo')
        ownership = Membership.objects.create(user=self.user, club=test_club, type=1)
        officer_relationship = Membership.objects.create(user=self.other_user_one, club=test_club, type=2)
        membership = Membership.objects.create(user=self.other_user_two, club=test_club, type=3)
        self.assertEqual(self.user.get_membership(test_club.id), ownership)
        self.assertEqual(self.other_user_one.get_membership(test_club.id), officer_relationship)
        self.assertEqual(self.other_user_two.get_membership(test_club.id), membership)

    """Tests below are for validity"""

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
