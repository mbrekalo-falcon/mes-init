from django.urls import path

from .views import UserView

MAIN_PATH = 'users'

urlpatterns = [
    path(MAIN_PATH, UserView.as_view()),
]