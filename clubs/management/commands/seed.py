from random import randint, choice

import django.db.utils
from django.core.management.base import BaseCommand
from faker import Faker

from clubs.models import User, Club, Membership, Application, Tournament, TournamentMembers


# !!! Certain users have to be added
# !!! Needs tournaments to be added
class Command(BaseCommand):
    """The database seeder."""
    USER_COUNT = 75  # Use to add this many fake users to database
    CLUB_COUNT = 2  # Use to add this many fake users to database
    # Password for every user seeded into the database
    DEFAULT_PASSWORD = 'Password123'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    # Creates a user using fake data
    def create_user_seed(self):
        fake_email = self.faker.unique.email()
        fake_name = self.faker.name()
        random_exp = randint(1, 4)
        fake_bio = self.faker.text(max_nb_chars=520)
        User.objects.create_user(
            email=fake_email,
            password=self.DEFAULT_PASSWORD,
            name=fake_name,
            experience=random_exp,
            bio=fake_bio
        )

    # Seeds user
    def seed_user(self):
        user_count = 0
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}', end='\r')
            try:
                self.create_user_seed()
            except django.db.utils.IntegrityError:
                continue
            user_count += 1
        print('User seeding complete')

    # Seeds 5 applicants and 10 memberships of different types into the club
    def seed_applicants_and_memberships(self, club, club_owner):
        fake_statement = self.faker.text(max_nb_chars=50)
        potential_applicants = list(User.objects.all())
        potential_applicants.remove(club_owner)
        for i in range(5):
            random_user = choice(potential_applicants)
            club_application = Application.objects.get_or_create(
                user=random_user,
                club=club,
                statement=fake_statement,
                status='pending'
            )
            potential_applicants.remove(random_user)
        for i in range(10):
            random_user = choice(potential_applicants)
            random_user_type = randint(2, 3)
            club_member = Membership.objects.create(
                user=random_user,
                club=club,
                type=random_user_type
            )
            potential_applicants.remove(random_user)

    # Creates a club using fake data, makes 5 applications, makes 10 members
    def create_club_seed(self):
        random_user = choice(User.objects.all())
        club_name = create_club_name(random_user)
        # Using Bush House as a default location for now, can be changed later if necessary
        fake_location = "Bush House"
        fake_description = self.faker.text(max_nb_chars=520)
        club_seed = Club.objects.create(
            name=club_name,
            location=fake_location,
            description=fake_description,
        )
        club_owner_membership = Membership.objects.create(
            user=random_user,
            club=club_seed,
            type=1
        )
        self.seed_applicants_and_memberships(club_seed, random_user)

    # Seeds club
    def seed_club(self):
        club_count = 0
        while club_count < Command.CLUB_COUNT:
            print(f'Seeding club {club_count}', end='\r')
            try:
                self.create_club_seed()
            except django.db.utils.IntegrityError:
                continue
            club_count += 1
        print('Club seeding complete')

    # Seed gravatar user and club
    def seed_gravatar(self):
        if User.objects.filter(email__exact="getgoogle@hotmail.com"):
            pass
        else:
            print(f'Seeding gravatar', end='\r')
            gravatar_user = User.objects.create_user(
                # This is not a fake email, but it is an inactive email that has been set up for this purpose and has a
                # gravatar account associated with it
                email="getgoogle@hotmail.com",
                name="Grace Gravatar",
                password=self.DEFAULT_PASSWORD,
                experience=2,
                bio="This account has been purposely seeded to show the working of gravatar. :)"
            )
            gravatar_club = Club.objects.create(
                name="Gravatar Club",
                location="Bush House",
                description="This club is to demonstrate the working of gravatar",
                # no users in the club
            )
            gravatar_membership = Membership.objects.create(
                user=gravatar_user,
                club=gravatar_club,
                type=1
            )
            self.seed_applicants_and_memberships(gravatar_club, gravatar_user)
            print('Gravatar seeding complete')

    def seed_set_user_one(self):
        user = User.objects.create_user(
            email="jeb@example.org",
            name="Jebediah Kerman",
            password=self.DEFAULT_PASSWORD
        )
        return user

    def seed_set_user_two(self):
        user = User.objects.create_user(
            email="val@example.org",
            name="Valentina Kerman",
            password=self.DEFAULT_PASSWORD
        )
        return user

    def seed_set_user_three(self):
        user = User.objects.create_user(
            email="billie@example.org",
            name="Billie Kerman",
            password=self.DEFAULT_PASSWORD
        )
        return user

    def seed_set_data(self):
        """Create set clubs, if not in database"""
        # c = created is a boolean
        kerbal_chess_club, created = Club.objects.get_or_create(
            name="Kerbal Chess Club",
            location="Bush House",
            description="Founded by B. Kerman",
        )
        if created:
            print(f'Seeding set data', end='\r')
        additional_club_one, one_created = Club.objects.get_or_create(
            name="PEP Chess Club",
            location="Bush House",
            description="C++ and Scala",
        )
        if one_created:
            one_owner = choice(User.objects.all())
            Membership.objects.create(
                user=one_owner,
                club=additional_club_one,
                type=1
            )
        additional_club_two, two_created = Club.objects.get_or_create(
            name="INS Chess Club",
            location="Bush House",
            description="Wireshark and HTML",
        )
        additional_club_three, three_created = Club.objects.get_or_create(
            name="SEG Chess Club",
            location="Bush House",
            description="Python and Django",
        )
        if three_created:
            three_owner = choice(User.objects.all())
            Membership.objects.create(
                user=three_owner,
                club=additional_club_three,
                type=1
            )

        if User.objects.filter(email__exact="jeb@example.org"):
            pass
        else:
            jebediah = self.seed_set_user_one()
            Membership.objects.get_or_create(
                user=jebediah,
                club=kerbal_chess_club,
                type=3
            )
            Membership.objects.get_or_create(
                user=jebediah,
                club=additional_club_one,
                type=2
            )

        if User.objects.filter(email__exact="val@example.org"):
            pass
        else:
            valentina = self.seed_set_user_two()
            Membership.objects.get_or_create(
                user=valentina,
                club=kerbal_chess_club,
                type=2
            )
            Membership.objects.get_or_create(
                user=valentina,
                club=additional_club_two,
                type=1
            )

        if User.objects.filter(email__exact="billie@example.org"):
            pass
        else:
            billie = self.seed_set_user_three()
            Membership.objects.get_or_create(
                user=billie,
                club=kerbal_chess_club,
                type=1
            )
            Membership.objects.get_or_create(
                user=billie,
                club=additional_club_three,
                type=3
            )
        if created:
            print('Set data seeding complete')

    # Seeds the database
    def handle(self, *args, **options):
        self.stdout.write("seeding data...")
        self.seed_user()
        self.seed_set_data()
        self.seed_club()
        self.seed_gravatar()
        self.stdout.write("done")


# Creates the club name using the club owners name
def create_club_name(user):
    club_name = f'{user.name}\'s Club'
    return club_name
