from django.test import TestCase
from clubs.models import Tournament, User, Club, Membership, TournamentMembers


class TournamentMembersModelTestCase(TestCase):
    """Unit tests for the Tournament members model."""
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.user = User.objects.get(email='petrapickles@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        ownership = Membership.objects.create(
            user=self.owner,
            club=self.club,
            type=1
        )
        self.tournament = Tournament.objects.create(
            name='test',
            organiser=self.owner,
            description='test',
            deadline='2026-10-25 14:30:59',
            capacity=3,
            club=self.club
        )

    def test_check_correct_creation(self):
        tournamentMember = TournamentMembers.objects.create(user=self.user, tournament=self.tournament)
        tournamentMember.name = tournamentMember.tournament.name
        self.assertEqual(tournamentMember.user, self.user)
        self.assertEqual(tournamentMember.tournament, self.tournament)
        self.assertEqual(tournamentMember.name, self.tournament.name)
