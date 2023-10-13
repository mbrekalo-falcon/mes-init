from django.urls import path

from .views import UserLoginView, ActivateAccountView, ResetPasswordView, SocialAuthView

MAIN_PATH = 'auth/'


urlpatterns = [
    path(MAIN_PATH+'login', UserLoginView.as_view()),

    # Activate account
    path(MAIN_PATH+'activate/<token_id>', ActivateAccountView.as_view()),

    # Reset password
    path(MAIN_PATH+'request-reset-password/<email>', ResetPasswordView.as_view()),  # Request
    path(MAIN_PATH+'reset-password/<token_id>', ResetPasswordView.as_view()),  # Set new password

    # Google AUTH
    path(MAIN_PATH+'social-auth', SocialAuthView.as_view())

]
