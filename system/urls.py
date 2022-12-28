"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('feed/', views.feed, name='feed'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('new_application/<int:club_id>/', views.new_application, name='new_application'),
    path('new_application/', views.new_application, name='new_application'),
    path('user/<int:user_id>', views.show_user, name='show_user'),
    path('users/', views.user_list, name='user_list'),
    path('view_applications/', views.view_applications, name='view_applications'),
    path('edit_application/<int:application_id>/', views.edit_application, name='edit_application'),
    path('edit_application/', views.edit_application, name='edit_application'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('create_club/', views.create_club, name='create_club'),
    path('club_list/', views.club_list, name='club_list'),
    path('change_password/', views.change_password, name='change_password'),
    path('my_clubs/', views.my_clubs, name='my_clubs'),
    path('my_clubs/<int:type>/', views.my_clubs, name='my_club'),
    path('view_app_to_club/<int:club_id>/', views.view_app_to_club, name='view_app_to_club'),
    path('change_app_status/<int:application_id>/<int:accept>/<int:club_id>/', views.change_app_status, name='change_app_status'),
    path('club_members/<int:club_id>/', views.club_members, name='club_members'),
    path('change_member_type/<int:user_id>/<int:club_id>/<int:promote>/', views.change_member_type, name='change_member_type'),
    path('create_tournament/<int:club_id>/', views.create_tournament, name='create_tournament'),
    path('tournament_list/', views.tournament_list, name='tournament_list'),
    path('sign_up_tournament/<int:tournament_id>/', views.sign_up_tournament, name='sign_up_tournament'),
    path('withdraw_tournament/<int:tournament_id>/', views.withdraw_tournament, name='withdraw_tournament'),
    path('club_profile/<int:club_id>/', views.club_profile, name='club_profile'),
]
