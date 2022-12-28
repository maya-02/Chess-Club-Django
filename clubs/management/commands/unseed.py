from typing import Text
from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club, Application


class Command(BaseCommand):
    def __init__(self):
        super().__init__()

    # Unseeds user, club and applications
    def handle(self, *args, **options):  # same as **kwargs
        self.stdout.write("unseeding users...")
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        self.stdout.write("unseeding clubs...")
        Club.objects.filter().delete()
        self.stdout.write("unseeding applications...")
        Application.objects.filter().delete()
        self.stdout.write("done")
