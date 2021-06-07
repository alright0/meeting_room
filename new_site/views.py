import json
from datetime import datetime

from django.contrib.auth.models import Group, User
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, request
from django.shortcuts import render
from django.utils import timezone

from .logic import formatted_time
from .models import Room, Schedule
from .forms import ScheduleForm, RoomForm, UserForm


# Create your views here.
def index(request):
    """Возвращает страницу со списком всех комнат и их описанием.
    Для менеджеров также возвращает список совещаний для подтверждения"""

    if request.method == "POST":

        if request.user.groups.filter(name="manager"):

            answer = request.POST.get("answer")
            meeting_id = request.POST.get("meeting_id")

            # здесь отклоняется или подтверждается встреча
            if answer:
                meet_id = int(meeting_id.replace("meeting_id_", ""))
                if answer == "accept":
                    this_meeting = Schedule.objects.get(id=meet_id)
                    this_meeting.status = True
                    this_meeting.save()
                    result = {"answer": "Встреча подтверждена!"}
                elif answer == "decline":
                    Schedule.objects.get(id=meet_id).delete()
                    result = {"answer": "Встреча отклонена!"}

                return HttpResponse(
                    json.dumps(result, cls=DjangoJSONEncoder),
                    content_type="application/json",
                )

            meetings_to_approve = json.dumps(
                Schedule.meetings_to_approve(request.user.id), cls=DjangoJSONEncoder
            )

        else:
            meetings_to_approve = json.dumps([{}])

        return HttpResponse(meetings_to_approve, content_type="application/json")

    rooms = Room.objects.all()
    schedule = Schedule.get_room_statuses(rooms)

    if request.user.groups.filter(name="manager"):
        meetings_to_approve = Schedule.meetings_to_approve(request.user.id)
    else:
        meetings_to_approve = None

    context = {
        "title": "Альфа Переговорки",
        "rooms": rooms,
        "schedule": schedule,
        "meetings_to_approve": meetings_to_approve,
    }

    return render(request, "new_site/index.html", context)


def room_schedule(request, room_id):
    """Возвращает страницу с расписанием комнаты"""

    if request.method == "POST":
        form = ScheduleForm(room_id, request.POST)
        if form.is_valid():

            new_meeting = Schedule(
                start_time=request.POST["start_time"],
                end_time=request.POST["end_time"],
                organizator_id=request.user,
                manager_id=User.objects.get(id=request.POST["manager_id"]),
                room_id=Room.objects.get(id=room_id),
                title=request.POST["title"],
            )
            new_meeting.save()

    else:
        form = ScheduleForm(room_id)

    room = Room.objects.get(id=room_id)
    schedule = Schedule.get_room_schedule(room)

    context = {
        "title": f"{room.name}. Расписание",
        "room": room,
        "schedule": schedule,
        "form": form,
    }

    return render(request, "new_site/room_schedule.html", context)


def coworkers(request):
    """Возвращает страницу управления группами пользователей"""

    form = UserForm()

    context = {"form": form}

    return render(request, "new_site/coworkers.html", context)


def add_room(request):
    """Возвращает страницу с формой создания комнаты"""
    if request.method == "POST":

        form = RoomForm(request.POST)

        if request.is_ajax():
            room = Room.objects.get(id=request.POST["id"])

            room_id = room.id
            room_name = room.name
            room_seats = room.seats
            room_board = room.board
            room_projector = room.projector
            room_description = room.description

            room_json = json.dumps(
                {
                    "id": room_id,
                    "name": room_name,
                    "seats": room_seats,
                    "board": room_board,
                    "projector": room_projector,
                    "description": room_description,
                },
                cls=DjangoJSONEncoder,
            )

            return HttpResponse(room_json, content_type="application/json")

        print(request.POST)

        if form.is_valid():
            room_exists = Room.objects.get(id=request.POST["name"])
            if room_exists:
                update_room = form.save(commit=False)
                room_exists.name = update_room.name
                room_exists.seats = update_room.seats
                room_exists.board = update_room.board
                room_exists.projector = update_room.projector
                room_exists.description = update_room.description
                room_exists.save()
            else:
                form.save()

    else:
        # rooms = Room.objects.all()

        # rooms_list = list(room.name for room in rooms)

        form = RoomForm()

    context = {"form": form}

    return render(request, "new_site/add_room.html", context)


def login(request):
    pass
