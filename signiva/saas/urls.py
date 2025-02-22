from django.contrib import admin
from .views import LoginView, SignupView, ResetPasswordView, \
                   ResetPasswordConfirmationView, MeView, \
                   InviteTeamMemberView, PrefillSignupView
from django.urls import path

urlpatterns = [
    path('login', LoginView.as_view()),
    path('signup', SignupView.as_view()),
    path('signup/prefill', PrefillSignupView.as_view()),
    path('passwd/reset', ResetPasswordView.as_view()),
    path('passwd/reset/cnfrm', ResetPasswordConfirmationView.as_view()),
    path('me', MeView.as_view()),
    path('invite', InviteTeamMemberView.as_view()),
]
