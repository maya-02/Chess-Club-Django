from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, User, Membership
from clubs.tests.helpers import reverse_with_next


class ChangeMemberTypeViewTest(TestCase):
    VIEW = 'change_member_type'

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.officer = User.objects.get(email='janedoe@example.org')
        self.member = User.objects.get(email='petrapickles@example.org')
        self.club = Club.objects.get(name='alpha_bravo')
        self.ownership = Membership.objects.create(
            user=self.owner,
            club=self.club,
            type=1
        )
        self.officer_relationship = Membership.objects.create(
            user=self.officer,
            club=self.club,
            type=2
        )
        self.membership = Membership.objects.create(
            user=self.member,
            club=self.club,
            type=3
        )
        self.promote_url = reverse(self.VIEW, kwargs={'user_id': self.member.id, 'club_id': self.club.id, 'promote': 1})
        self.demote_url = reverse(self.VIEW, kwargs={'user_id': self.officer.id, 'club_id': self.club.id, 'promote': 0})
        self.transfer_ownership_url = reverse(self.VIEW, kwargs={'user_id': self.officer.id, 'club_id': self.club.id,
                                                                 'promote': 2})

    def test_change_member_type_url(self):
        self.assertEqual(self.promote_url, f'/{self.VIEW}/{self.member.id}/{self.club.id}/1/')
        self.assertEqual(self.demote_url, f'/{self.VIEW}/{self.officer.id}/{self.club.id}/0/')
        self.assertEqual(self.transfer_ownership_url, f'/{self.VIEW}/{self.officer.id}/{self.club.id}/2/')

    def test_change_member_type_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.promote_url)
        response = self.client.get(self.promote_url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        redirect_url = reverse_with_next('log_in', self.demote_url)
        response = self.client.get(self.demote_url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_change_member_type_promote(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        member_before_count = Membership.objects.count()
        response = self.client.get(self.promote_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.type, 2)

    def test_successful_change_member_type_demote(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        member_before_count = Membership.objects.count()
        response = self.client.get(self.demote_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count)
        self.officer_relationship.refresh_from_db()
        self.assertEqual(self.officer_relationship.type, 3)

    def test_unsuccessful_change_member_type_promote(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        bad_promote_url = reverse(self.VIEW, kwargs={'user_id': self.officer.id, 'club_id': self.club.id, 'promote': 1})
        member_before_count = Membership.objects.count()
        response = self.client.get(bad_promote_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count)
        self.membership.refresh_from_db()
        self.assertEqual(self.officer_relationship.type, 2)

    def test_unsuccessful_change_member_type_demote(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        bad_demote_url = reverse(self.VIEW, kwargs={'user_id': self.member.id, 'club_id': self.club.id, 'promote': 0})
        member_before_count = Membership.objects.count()
        response = self.client.get(bad_demote_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.type, 3)

    def test_bad_membership_change_member_type(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        bad_user = User.objects.get(email='peterpickles@example.org')
        bad_membership = Membership.objects.create(user=bad_user, club=self.club, type=4)
        bad_url = reverse(self.VIEW, kwargs={'user_id': bad_user.id, 'club_id': self.club.id, 'promote': 1})
        member_before_count = Membership.objects.count()
        response = self.client.get(bad_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count)
        self.membership.refresh_from_db()
        self.assertEqual(bad_membership.type, 4)

    def test_successful_change_member_type_transfer_ownership(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        member_before_count = Membership.objects.count()
        response = self.client.get(self.transfer_ownership_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count)
        self.ownership.refresh_from_db()
        self.officer_relationship.refresh_from_db()
        self.assertEqual(self.officer_relationship.type, 1)
        self.assertEqual(self.ownership.type, 2)

    def test_unsuccessful_change_member_type_transfer_ownership(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        member_before_count = Membership.objects.count()
        bad_transfer_ownership_url = reverse(self.VIEW,
                                             kwargs={'user_id': self.member.id, 'club_id': self.club.id, 'promote': 2})
        response = self.client.get(bad_transfer_ownership_url)
        member_after_count = Membership.objects.count()
        self.assertEqual(member_after_count, member_before_count)
        self.ownership.refresh_from_db()
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.type, 3)
        self.assertEqual(self.ownership.type, 1)
