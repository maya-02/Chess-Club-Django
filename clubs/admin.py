from django.contrib import admin
from .models import Membership, User, Application, Club, Tournament, TournamentMembers


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name',
                    'id']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'statement']


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'club',
                    'type']


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name',
                    'club',
                    'deadline',
                    'capacity'
                    ]

@admin.register(TournamentMembers)
class TournamentMembersAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'tournament']
