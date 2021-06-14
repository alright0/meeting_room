import json
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import LoginForm, RoomForm, ScheduleForm, UserForm
from .logic import parse_meeting_id
from .models import Room, Schedule


@login_required
def index(request):
    """Возвращает страницу со списком всех комнат и их описанием.
    Для менеджеров также возвращает список совещаний для подтверждения"""

    if request.method == "POST":
        if request.user.groups.filter(name="manager"):

            # здесь отклоняется или подтверждается встреча
            answer = request.POST.get("answer")
            if answer:
                meet_id = parse_meeting_id(request.POST.get("meeting_id"))
                meeting_details = Schedule.meeting_details(meet_id)
                this_meeting = Schedule.objects.get(id=meet_id)
                this_meeting.status = True if answer == "accept" else False
                this_meeting.save()

                return HttpResponse(
                    json.dumps(
                        {"organizator_id": meeting_details["organizator_id"]},
                        cls=DjangoJSONEncoder,
                    ),
                    content_type="application/json",
                )

            meetings_to_approve = json.dumps(
                Schedule.meetings_to_approve(request.user.id), cls=DjangoJSONEncoder
            )

            return HttpResponse(meetings_to_approve, content_type="application/json")

    rooms = Room.objects.all()
    schedule = Schedule.get_room_statuses(rooms)
    context = {
        "rooms": rooms,
        "schedule": schedule,
    }

    return render(request, "new_site/index.html", context)


@login_required
def room_schedule(request, room_id):
    """Возвращает страницу с расписанием комнаты"""

    form_is_open = "hidden=true"

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

        form_is_open = ""

    else:
        form = ScheduleForm(room_id)

    room = Room.objects.get(id=room_id)
    schedule = Schedule.get_room_schedule(room)

    context = {
        "room": room,
        "schedule": schedule,
        "form": form,
        "form_is_open": form_is_open,
    }

    return render(request, "new_site/room_schedule.html", context)


@login_required
@permission_required("auth.change_user", login_url="/login/")
def coworkers(request):
    """Возвращает страницу управления группами пользователей"""

    if request.method == "POST":
        manager_group = Group.objects.get(name="manager")
        user_id = request.POST["user"]
        if user_id and request.is_ajax():
            is_manager = Group.objects.filter(user=user_id, name="manager").first()
            manager = {"manager": True if is_manager else False}
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
@permission_required("new_site.add_room", login_url="/login/")
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
                    # Обновление существущей комнаты
                    update_room = form.save(commit=False)
                    room_exists.name = update_room.name
                    room_exists.seats = update_room.seats
                    room_exists.board = update_room.board
                    room_exists.projector = update_room.projector
                    room_exists.description = update_room.description
                    room_exists.save()
                else:
                    # создание новой комнаты
                    form.save()
                return redirect("/")

    context = {"form": form}

    return render(request, "new_site/add_room.html", context)


def log_in(request):
    """Возвращает форму логина"""

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data["username"], password=data["password"])
            if user and user.is_active:
                login(request, user)
    else:
        form = LoginForm()

    context = {"form": form}

    return render(request, "new_site/login.html", context)
