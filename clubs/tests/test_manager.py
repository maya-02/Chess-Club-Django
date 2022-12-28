"""Unit tests for the User Manager."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User


class UserManagerTestCase(TestCase):

    def setUp(self):
        self.super_user = User.objects.create_superuser(email='superuser@example.org', password='Admin123')

    def test_email_must_not_be_blank(self):
        self.super_user.email = ''
        self._assert_user_is_invalid()

    def test__create_user_raises_value_error(self):
        self.assertRaises(ValueError, lambda: User.objects._create_user(email='', password='Admin123'))

    def test_is_staff(self):
        self.assertTrue(self.super_user.is_staff)

    def test_is_staff_raises_value_error(self):
        self.assertRaises(ValueError,
                          lambda: User.objects.create_superuser(email='superuser@example.org', password='Admin123',
                                                                is_staff=False))

    def test_is_super_user(self):
        self.assertTrue(self.super_user.is_superuser)

    def test_is_superuser_raises_value_error(self):
        self.assertRaises(ValueError,
                          lambda: User.objects.create_superuser(email='superuser@example.org', password='Admin123',
                                                                is_superuser=False))

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.super_user.full_clean()
