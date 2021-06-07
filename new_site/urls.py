from django.urls import path
from . import views

app_name = "new_site"
urlpatterns = [
    path("", views.index, name="index"),
    path("rooms/<int:room_id>", views.room_schedule, name="room_schedule"),
    path("coworkers", views.coworkers, name="coworkers"),
    path("addroom", views.add_room, name="add_room"),
]
