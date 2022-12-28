import django
import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from .models import TournamentMembers, User, Application, Club, Membership, Tournament
from django.shortcuts import redirect, render, get_object_or_404
from clubs.helpers import login_prohibited
from .forms import SignUpForm, ApplicationForm, ClubForm, LogInForm, ProfileForm, PasswordForm, TournamentForm

@login_prohibited
def home(request):
    return render(request, 'home.html')


@login_required
def feed(request):
    return render(request, 'feed.html', {'user': request.user})


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
def change_password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('feed')
    form = PasswordForm()
    return render(request, 'change_password.html', {'form': form})


@login_required()
def edit_profile(request):
    instance = get_object_or_404(User, email=request.user.email)
    form = ProfileForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('feed')
    return render(request, 'edit_profile.html', {'form': form})


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                redirect_url = request.POST.get('next') or 'feed'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "incorrect email or password")

    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form})


@login_required
def log_out(request):
    logout(request)
    return redirect('home')


@login_required
def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        return render(request, 'show_user.html', {'user': user})


@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


@login_required
def new_application(request, club_id):
    form = ApplicationForm(request.POST or None)
    if request.method == 'POST':
        if request.user.is_authenticated:
            club = Club.objects.get(id=club_id)
            if form.is_valid():
                form.save(request.user, club)
                return redirect('club_list')
    return render(request, 'new_application.html', {'form': form, 'club_id': club_id})


@login_required
def view_applications(request):
    user = User.objects.get(id=request.user.id)
    applications = user.application_set.all()
    return render(request, 'view_applications.html', {'applications': applications})


@login_required
def edit_application(request, application_id):
    instance = get_object_or_404(Application, id=application_id)
    form = ApplicationForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            return redirect('view_applications')
    return render(request, 'edit_application.html', {'form': form, 'application_id': application_id})


@login_required
def create_club(request):
    form = ClubForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(request.user)
            return redirect('feed')
    return render(request, 'create_club.html', {'form': form})


@login_required
def club_profile(request, club_id):
    club = Club.objects.get(id=club_id)
    return render(request, 'club_profile.html', {'club': club})


@login_required
def club_list(request):
    applied = request.user.application_set.all()
    clubs = [j for j in Club.objects.all() if j not in [i.club for i in applied]]
    return render(request, 'club_list.html', {'clubs': clubs})


@login_required
def my_clubs(request, type=None):
    response_dict = {0: 'anything',
                     1: 'owner',
                     2: 'officer', 
                     3: 'member'}
    if type and type > 0: 
        memberships = Membership.objects.filter(user=request.user, type=type) or None
    else:
        memberships = request.user.membership_set.all()
    if memberships:
        return render(request, 'my_clubs.html', {'memberships': memberships})
    return render(request, 'my_clubs.html', {'type': response_dict[type] if type is not None else ''})


@login_required
def view_app_to_club(request, club_id):
    applications = [i for i in Club.objects.get(id=club_id).application_set.all() if
                    i in Application.objects.filter(status='pending')]
    return render(request, 'view_app_to_club.html', {'applications': applications})


@login_required
def change_app_status(request, application_id, accept, club_id):
    application = get_object_or_404(Application, id=application_id)
    if accept:
        application.status = 'accepted'
        Membership.objects.create(user=application.user, club=application.club, statement=application.statement, type=3)
    else:
        application.status = 'rejected'
    application.save()
    applications = [i for i in Club.objects.get(id=club_id).application_set.all() if
                    i in Application.objects.filter(status='pending')]
    return render(request, 'view_app_to_club.html', {'applications': applications})


@login_required
def club_members(request, club_id):
    memberships = Club.objects.get(id=club_id).membership_set.all()
    return render(request, 'club_members.html',
                  {'memberships': memberships, 'type': request.user.get_membership(club_id).type, 'user': request.user})


@login_required
def change_member_type(request, user_id, club_id, promote):
    membership = get_object_or_404(User, id=user_id).get_membership(club_id)
    if 0 < membership.type < 4:
        if promote == 1 and membership.type != 2:
            membership.type -= 1
        elif promote == 0 and membership.type != 3:
            membership.type += 1
        elif promote == 2 and membership.type == 2:
            owner_membership = get_object_or_404(Membership, user=request.user, club=Club.objects.get(id=club_id))
            membership.type = 1
            owner_membership.type = 2
            owner_membership.save()
        membership.save()
    return redirect('club_members', club_id)


@login_required
def tournament_list(request):
    tournaments = [j for j in [Tournament.objects.filter(club=i.club) for i in request.user.membership_set.all()]]
    return render(request, "tournament_list.html", {'tournaments': tournaments, 'user': request.user})


@login_required
def create_tournament(request, club_id):
    membership = request.user.get_membership(club_id)
    if membership.type == 2 or membership.type == 1:
        form = TournamentForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                form.save(Club.objects.get(id=club_id), request.user)
                return redirect('my_clubs')
        return render(request, 'create_tournament.html', {'form': form, 'club_id': club_id, 'today': datetime.datetime.now()})
    return redirect('my_clubs')


@login_required
def sign_up_tournament(request, tournament_id):
    if not Tournament.objects.get(id=tournament_id).is_contestant(request.user):
        TournamentMembers.objects.create(user=request.user, tournament=Tournament.objects.get(id=tournament_id))
    return redirect('tournament_list')


@login_required
def withdraw_tournament(request, tournament_id):
    TournamentMembers.objects.get(user=request.user, tournament=Tournament.objects.get(id=tournament_id)).delete()
    return redirect('tournament_list')
