from django import forms
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.core.validators import RegexValidator
from clubs.models import Club, User, Application, Membership, Tournament, TournamentMembers
import datetime


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'email'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'password'}))


class SignUpForm(forms.ModelForm):
    LEVEL = [
        (1, 'beginner'),
        (2, 'intermediate'),
        (3, 'advanced'),
        (4, 'magnus carlson'),
    ]
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'email'}))
    name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'name'}))
    experience = forms.ChoiceField(label='', choices=LEVEL)
    bio = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'bio'}))
    class Meta:
        model = User
        fields = ['email', 'name', 'experience', 'bio']

    new_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'password'}),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'confirm password'}))

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        super().save(commit=False)
        try:
            user = User.objects.create_user(
                email=self.cleaned_data.get('email'),
                password=self.cleaned_data.get('new_password'),
                name=self.cleaned_data.get('name'),
                experience=self.cleaned_data.get('experience'),
                bio=self.cleaned_data.get('bio')
            )
            return user

        except IntegrityError as e:
            super().save()


class ProfileForm(forms.ModelForm):
    """Form to update profile."""

    class Meta:
        model = User
        fields = ['email', 'name', 'experience', 'bio']


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['statement']

    def save(self, user=None, club=None):
        super().save(commit=False)
        try:
            application = Application.objects.create(
                    user=user,
                    club=club,
                    statement=self.cleaned_data.get('statement'),
                    status='pending'
            )
            return application

        except IntegrityError as e:
            super().save()


class PasswordForm(forms.Form):
    """Form enabling users to change their password."""
    password = forms.CharField(label='Current Password',
                               widget=forms.PasswordInput())  # Confirmation that it is the user trying to change their password
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'location', 'description']

    def save(self, user):
        super().save(commit=False)
        club = Club.objects.create(
            name=self.cleaned_data.get('name'),
            location=self.cleaned_data.get('location'),
            description=self.cleaned_data.get('description')
        )
        Membership.objects.create(
            user=user,
            club=club,
            type=1
        )

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'description']

    deadline = forms.DateField(label='Deadline',widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    capacity=forms.IntegerField(label='Capacity',widget = forms.widgets.NumberInput(attrs = {
      'min': 2,
      'max':96,
      'value': 2,
      'type': 'number',
      'style': 'max-width: 6em'
    }))

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline < datetime.date.today():
            raise forms.ValidationError("The deadline cannot be in the past!")
        return deadline

    def clean_capacity(self):
        capacity = self.cleaned_data['capacity']
        if capacity < 2 or capacity > 96:
            raise forms.ValidationError("The capacity must be between 2 and 96")
        return capacity

    def save(self, club, user):
        super().save(commit=False)
        tournament = Tournament.objects.create(
            name=self.cleaned_data.get('name'),
            description=self.cleaned_data.get('description'),
            deadline=self.cleaned_data.get('deadline'),
            capacity=self.cleaned_data.get('capacity'),
            club=club,
            organiser=user
        )
        return tournament
