from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Tournament, User, Club, Membership, TournamentMembers


class TournamentModelTestCase(TestCase):
    """Unit tests for the Tournament model."""
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.user_one = User.objects.get(email='petrapickles@example.org')
        self.user_two = User.objects.get(email='peterpickles@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        ownership = Membership.objects.create(
            user=self.owner,
            club=self.club,
            type=1
        )
        officer_relationship = Membership.objects.create(
            user=self.user_one,
            club=self.club,
            type=2
        )
        self.tournament = Tournament.objects.create(
            name='test',
            organiser=self.owner,
            description='test',
            deadline='2026-10-25 14:30:59',
            capacity=3,
            club=self.club
        )

    def test_valid_tournament(self):
        self._assert_tournament_is_valid()

    def test_num_of_contestants(self):
        before_count = self.tournament.num_of_contestants()
        self.assertEqual(before_count, 0)
        tournamentMember = TournamentMembers.objects.create(user=self.user_one, tournament=self.tournament)
        after_count = self.tournament.num_of_contestants()
        self.assertEqual(after_count, before_count + 1)

    def test_contestants(self):
        before_count = len(self.tournament.contestants())
        self.assertEqual(before_count, 0)
        tournamentMember = TournamentMembers.objects.create(user=self.user_one, tournament=self.tournament)
        after_count = len(self.tournament.contestants())
        self.assertEqual(after_count, before_count + 1)

    def test_tournament_name_must_be_unique(self):
        second_tournament = Tournament.objects.create(
            name='test2',
            organiser=self.owner,
            description='test',
            deadline='2026-10-25 14:30:59',
            capacity=3,
            club=self.club)
        self.tournament.name = second_tournament.name
        self._assert_tournament_is_invalid()

    def test_tournament_name_must_not_be_blank(self):
        self.tournament.name = ''
        self._assert_tournament_is_invalid()

    def test_tournament_name_may_contain_100_characters(self):
        self.tournament.name = 'x' * 100
        self._assert_tournament_is_valid()

    def test_tournament_name_must_not_contain_more_than_100_characters(self):
        self.tournament.name = 'x' * 101
        self._assert_tournament_is_invalid()

    def test_tournament_description_must_not_be_blank(self):
        self.tournament.description = ''
        self._assert_tournament_is_invalid()

    def test_tournament_description_may_contain_520_characters(self):
        self.tournament.description = 'x' * 520
        self._assert_tournament_is_valid()

    def test_tournament_description_must_not_contain_more_than_520_characters(self):
        self.tournament.description = 'x' * 521
        self._assert_tournament_is_invalid()

    def test_tournament_capacity_must_not_be_blank(self):
        self.tournament.capacity = ''
        self._assert_tournament_is_invalid()

    def test_tournament_capacity_may_be_2(self):
        self.tournament.capacity = 2
        self._assert_tournament_is_valid()

    def test_tournament_capacity_may_be_96(self):
        self.tournament.capacity = 96
        self._assert_tournament_is_valid()

    def test_tournament_capacity_may_not_be_less_than_2(self):
        self.tournament.capacity = 1
        self._assert_tournament_is_invalid()

    def test_tournament_capacity_may_not_be_more_than_96(self):
        self.tournament.capacity = 97
        self._assert_tournament_is_invalid()

    def test_tournament_deadline_may_be_in_the_future(self):
        self.tournament.deadline = '2025-10-25 14:30:59'
        self._assert_tournament_is_valid()

    def _assert_tournament_is_valid(self):
        try:
            self.tournament.full_clean()
        except (ValidationError):
            self.fail('Test tournament should be valid')

    def _assert_tournament_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()
