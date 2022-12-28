from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import DO_NOTHING
from django.shortcuts import get_object_or_404
from clubs.manager import UserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from libgravatar import Gravatar


class User(AbstractUser):
    LEVEL = [(1, 'beginner'),
            (2, 'intermediate'),
            (3, 'advanced'),
            (4, 'magnus carlson')]
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=False)
    experience = models.IntegerField(default=1, choices=LEVEL)
    bio = models.CharField(max_length=520, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def gravatar(self, size=120):
        """Return an URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar"""
        return self.gravatar(size=60)

    class Meta:
        ordering = ['experience']

    def get_membership(self, club_id):
        return get_object_or_404(Membership, user=self, club=Club.objects.get(id=club_id))
    
    def get_experience(self):
        return self.LEVEL[self.experience-1][1]


class Club(models.Model):
    name = models.CharField(max_length=20, blank=False)
    location = models.CharField(max_length=40, blank=False)
    description = models.CharField(max_length=520, blank=False)

    def get_club_owner(self):
        ownership = Membership.objects.get(club=self, type=1)
        return ownership.user

    def num_of_applications(self):
        return len([i for i in self.application_set.all() if i in Application.objects.filter(status='pending')])

    def num_of_members(self):
        return len(Membership.objects.filter(club=self))


class Application(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    statement = models.CharField(max_length=520, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, blank=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'club')


class Membership(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    statement = models.CharField(max_length=520, blank=True)
    type = models.IntegerField(3, blank=False)

    def get_type(self):
        type_dict = {1: 'owner',
                     2: 'officer',
                     3: 'member'}
        return type_dict[self.type]

    class Meta:
        ordering = ['type']
        unique_together = ('user', 'club')


class Tournament(models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True)
    organiser = models.ForeignKey('User', on_delete=models.CASCADE)
    description = models.CharField(max_length=520, blank=False)
    deadline = models.DateTimeField(blank=False)
    capacity = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(96)])
    organiser = models.ForeignKey('User', on_delete=DO_NOTHING)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=True)

    def num_of_contestants(self):
        return len([i for i in TournamentMembers.objects.filter(tournament=self)])
    
    def is_contestant(self, user):
        try:
            contestant = TournamentMembers.objects.get(user=user, tournament=self)
            return contestant
        except TournamentMembers.DoesNotExist:
            return False
    
    def contestants(self):
        return [i.user for i in TournamentMembers.objects.filter(tournament=self)]

class TournamentMembers(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'tournament')
