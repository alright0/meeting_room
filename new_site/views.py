import json
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.models import Group, User
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, request
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import LoginForm, RoomForm, ScheduleForm, UserForm
from .logic import formatted_time
from .models import Room, Schedule


# Create your views here.
@login_required
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
                meeting_details = Schedule.meeting_details(meet_id)

                if answer == "accept":
                    this_meeting = Schedule.objects.get(id=meet_id)
                    this_meeting.status = True
                    this_meeting.save()
                    result = {
                        "answer": "Встреча подтверждена!",
                        "organizator_id": meeting_details["organizator_id"],
                    }
                elif answer == "decline":
                    Schedule.objects.get(id=meet_id).delete()
                    result = {
                        "answer": "Встреча отклонена!",
                        "organizator_id": meeting_details["organizator_id"],
                    }

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
        "rooms": rooms,
        "schedule": schedule,
        "meetings_to_approve": meetings_to_approve,
    }

    return render(request, "new_site/index.html", context)


@login_required
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
            return redirect("/")

    else:
        form = ScheduleForm(room_id)

    room = Room.objects.get(id=room_id)
    schedule = Schedule.get_room_schedule(room)

    context = {
        "room": room,
        "schedule": schedule,
        "form": form,
    }

    return render(request, "new_site/room_schedule.html", context)


@login_required
@permission_required("change_user")
def coworkers(request):
    """Возвращает страницу управления группами пользователей"""

    if request.method == "POST":
        manager_group = Group.objects.get(name="manager")
        user_id = request.POST["user"]
        if user_id and request.is_ajax():
            is_manager = Group.objects.filter(user=user_id, name="manager").first()
            if is_manager:
                manager = {"manager": True}
            else:
                manager = {"manager": False}
            return HttpResponse(
                json.dumps(manager, cls=DjangoJSONEncoder),
                content_type="application/json",
            )

        elif user_id:
            user_in_group = Group.objects.filter(user=user_id, name="manager")
            if "groups" in request.POST.keys():
                if not user_in_group:
                    manager_group.user_set.add(user_id)
            else:
                if user_in_group:
                    manager_group.user_set.remove(user_id)

    form = UserForm()

    context = {"form": form}

    return render(request, "new_site/coworkers.html", context)


@login_required
@permission_required("add_room")
def add_room(request):
    """Возвращает страницу с формой создания комнаты"""

    form = RoomForm()

    if request.method == "POST":
        form = RoomForm(request.POST)

        # Этот участок возвращает информацию о комнате
        if request.is_ajax():
            room_info = Room.get_room_info(request.POST["id"])
            room_json = json.dumps(room_info, cls=DjangoJSONEncoder)

            return HttpResponse(room_json, content_type="application/json")

        # удаляет комнату
        if "delete" in request.POST.keys():
            room = Room.objects.get(id=int(request.POST["id"]))
            if room:
                room.delete()

                return HttpResponse(
                    json.dumps(
                        {"response": "deleted"},
                        cls=DjangoJSONEncoder,
                    ),
                    content_type="application/json",
                )

        # обновляет или добавляет комнату
        if "add" in request.POST.keys():
            if form.is_valid():
                try:
                    room_exists = Room.objects.get(id=request.POST["id"])
                except:
                    room_exists = None

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
                return redirect("/")

    context = {"form": form}

    return render(request, "new_site/add_room.html", context)


def login(request):

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data["username"], password=data["password"])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("Authenticated successfully")
                else:
                    return HttpResponse("Disabled account")
            else:
                return HttpResponse("Invalid login")
    else:
        form = LoginForm()

    context = {"form": form}

    return render(request, "new_site/login.html", context)
