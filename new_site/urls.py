from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "new_site"
urlpatterns = [
    path("", views.index, name="index"),
    path("rooms/<int:room_id>", views.room_schedule, name="room_schedule"),
    path("coworkers/", views.coworkers, name="coworkers"),
    path("addroom/", views.add_room, name="add_room"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="new_site/login.html"),
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        {"next_page": settings.LOGOUT_REDIRECT_URL},
        name="logout",
    ),
]
